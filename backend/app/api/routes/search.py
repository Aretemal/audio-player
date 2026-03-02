import logging
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.auth.dependencies import get_user_from_request, verify_auth_global

logger = logging.getLogger(__name__)
from app.db.session import get_db
from app.models.user import User
from app.models.song import Song, user_song_association
from app.models.album import Album
from app.models.playlist import Playlist
from app.schemas.song import SongRead
from app.schemas.album import AlbumRead
from app.schemas.playlist import PlaylistRead
from app.crud import bookmark as bookmark_crud
from app.services.musicbrainz import MusicBrainzService
from app.services import itunes as itunes_service
from app.services import deezer as deezer_service

router = APIRouter(
    prefix="/search",
    tags=["search"],
    dependencies=[Depends(verify_auth_global)],
)


@router.get("/", response_model=dict)
def search(
    q: str = Query(..., description="Поисковый запрос"),
    categories: Optional[str] = Query(None, description="Категории через запятую: songs,albums,playlists,artists"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    user_id = getattr(current_user, "id", None)
    logger.info("search (local): q=%r categories=%r skip=%s limit=%s user_id=%s", q, categories, skip, limit, user_id)
    if not q or len(q.strip()) < 1:
        logger.info("search (local): empty q, return empty")
        return {
            "songs": [],
            "albums": [],
            "playlists": [],
            "artists": [],
        }

    search_query = f"%{q.strip()}%"
    results = {
        "songs": [],
        "albums": [],
        "playlists": [],
        "artists": [],
    }

    if categories:
        categories_list = [c.strip().lower() for c in categories.split(",")]
    else:
        categories_list = ["songs", "albums", "playlists", "artists"]

    if "songs" in categories_list:
        songs_query = db.query(Song).join(Song.users).filter(
            and_(
                User.id == current_user.id,
                or_(
                    Song.title.ilike(search_query),
                    Song.artist.ilike(search_query),
                )
            )
        ).distinct()
        
        songs = songs_query.offset(skip).limit(limit).all()
        for song in songs:
            album_name = song.album.title if song.album else None
            results["songs"].append(SongRead(
                id=song.id,
                title=song.title,
                artist=song.artist,
                src=song.src,
                album=album_name,
                file_size=song.file_size,
                user_ids=[user.id for user in song.users],
                created_at=song.created_at,
                updated_at=song.updated_at,
            ))

    if "albums" in categories_list:
        albums_query = db.query(Album).join(Album.users).filter(
            and_(
                User.id == current_user.id,
                or_(
                    Album.title.ilike(search_query),
                    Album.creator.ilike(search_query),
                )
            )
        ).distinct()
        
        albums = albums_query.offset(skip).limit(limit).all()
        for album in albums:
            results["albums"].append(AlbumRead(
                id=album.id,
                title=album.title,
                creator=album.creator,
                song_ids=[song.id for song in album.songs],
                user_ids=[user.id for user in album.users],
                created_at=album.created_at,
                updated_at=album.updated_at,
            ))

    if "playlists" in categories_list:
        playlists_query = db.query(Playlist).join(Playlist.users).filter(
            and_(
                User.id == current_user.id,
                or_(
                    Playlist.title.ilike(search_query),
                    Playlist.description.ilike(search_query),
                )
            )
        ).distinct()
        
        playlists = playlists_query.offset(skip).limit(limit).all()
        for playlist in playlists:
            results["playlists"].append(PlaylistRead(
                id=playlist.id,
                title=playlist.title,
                description=playlist.description,
                song_ids=[song.id for song in playlist.songs],
                user_ids=[user.id for user in playlist.users],
                created_at=playlist.created_at,
                updated_at=playlist.updated_at,
            ))

    if "artists" in categories_list:
        artists_query = db.query(Song.artist).join(Song.users).filter(
            and_(
                User.id == current_user.id,
                Song.artist.isnot(None),
                Song.artist.ilike(search_query),
            )
        ).distinct()

        artists = artists_query.offset(skip).limit(limit).all()
        for artist_name in artists:
            if artist_name[0]:
                artist_songs_count = db.query(Song).join(Song.users).filter(
                    and_(
                        User.id == current_user.id,
                        Song.artist == artist_name[0],
                    )
                ).count()
                
                results["artists"].append({
                    "name": artist_name[0],
                    "songs_count": artist_songs_count,
                })

    logger.info(
        "search (local): result counts songs=%s albums=%s playlists=%s artists=%s",
        len(results["songs"]),
        len(results["albums"]),
        len(results["playlists"]),
        len(results["artists"]),
    )
    return results


def _normalize_songs(provider: str, data: dict, cat: str) -> tuple[list, int]:
    items = []
    if provider == "musicbrainz" and cat == "songs":
        for r in data.get("recordings", []):
            length_ms = r.get("length")
            items.append({
                "id": r.get("id"),
                "title": r.get("title"),
                "artist": r.get("artist"),
                "album": None,
                "preview_url": r.get("preview_url"),
                "artwork_url": None,
                "duration_ms": length_ms,
                "provider": "musicbrainz",
                "item_type": "song",
            })
        return items, data.get("total", 0)
    if provider == "itunes" and cat == "songs":
        for r in data.get("results", []):
            items.append({
                "id": str(r.get("trackId", "")),
                "title": r.get("trackName"),
                "artist": r.get("artistName"),
                "album": r.get("collectionName"),
                "preview_url": r.get("previewUrl"),
                "artwork_url": r.get("artworkUrl100") or r.get("artworkUrl60"),
                "duration_ms": r.get("trackTimeMillis"),
                "provider": "itunes",
                "item_type": "song",
            })
        return items, data.get("total", 0)
    if provider == "deezer" and cat == "songs":
        for t in data.get("data", []):
            artist = (t.get("artist") or {}).get("name", "")
            album_obj = t.get("album") or {}
            album = album_obj.get("title")
            cover = album_obj.get("cover_small") or album_obj.get("cover")
            items.append({
                "id": str(t.get("id", "")),
                "title": t.get("title"),
                "artist": artist,
                "album": album,
                "preview_url": t.get("preview"),
                "artwork_url": cover,
                "duration_ms": (t.get("duration") or 0) * 1000 if t.get("duration") else None,
                "provider": "deezer",
                "item_type": "song",
            })
        return items, data.get("total", 0)
    return items, 0


def _normalize_artists(provider: str, data: dict, db: Session, user_id: int) -> tuple[list, int]:
    items = []
    if provider == "musicbrainz":
        for a in data.get("artists", []):
            mbid = a.get("id") or ""
            existing = bookmark_crud.get_bookmark_by_musicbrainz_id(db, user_id, mbid, "artist")
            items.append({
                "id": mbid,
                "name": a.get("name"),
                "type": a.get("type"),
                "country": a.get("country"),
                "disambiguation": a.get("disambiguation"),
                "is_saved": existing is not None,
                "provider": "musicbrainz",
                "item_type": "artist",
            })
        return items, data.get("total", 0)
    if provider == "itunes":
        for r in data.get("results", []):
            ext_id = str(r.get("artistId", ""))
            existing = bookmark_crud.get_bookmark_by_musicbrainz_id(
                db, user_id, f"itunes:{ext_id}", "artist"
            ) if ext_id else None
            items.append({
                "id": ext_id,
                "name": r.get("artistName"),
                "type": None,
                "country": None,
                "disambiguation": None,
                "is_saved": existing is not None,
                "provider": "itunes",
                "item_type": "artist",
            })
        return items, data.get("total", 0)
    if provider == "deezer":
        for a in data.get("data", []):
            ext_id = str(a.get("id", ""))
            existing = bookmark_crud.get_bookmark_by_musicbrainz_id(
                db, user_id, f"deezer:{ext_id}", "artist"
            ) if ext_id else None
            items.append({
                "id": ext_id,
                "name": a.get("name"),
                "type": None,
                "country": None,
                "disambiguation": None,
                "is_saved": existing is not None,
                "provider": "deezer",
                "item_type": "artist",
            })
        return items, data.get("total", 0)
    return items, 0


def _normalize_albums(provider: str, data: dict, db: Session, user_id: int) -> tuple[list, int]:
    items = []
    if provider == "musicbrainz":
        for r in data.get("releases", []):
            mbid = r.get("id") or ""
            existing = bookmark_crud.get_bookmark_by_musicbrainz_id(db, user_id, mbid, "album")
            items.append({
                "id": mbid,
                "title": r.get("title"),
                "artist": r.get("artist"),
                "date": r.get("date"),
                "status": r.get("status"),
                "artwork_url": None,
                "is_saved": existing is not None,
                "provider": "musicbrainz",
                "item_type": "album",
            })
        return items, data.get("total", 0)
    if provider == "itunes":
        for r in data.get("results", []):
            ext_id = str(r.get("collectionId", ""))
            existing = bookmark_crud.get_bookmark_by_musicbrainz_id(db, user_id, f"itunes:{ext_id}", "album") if ext_id else None
            items.append({
                "id": ext_id,
                "title": r.get("collectionName"),
                "artist": r.get("artistName"),
                "date": r.get("releaseDate"),
                "status": None,
                "artwork_url": r.get("artworkUrl100") or r.get("artworkUrl60"),
                "is_saved": existing is not None,
                "provider": "itunes",
                "item_type": "album",
            })
        return items, data.get("total", 0)
    if provider == "deezer":
        for a in data.get("data", []):
            artist = (a.get("artist") or {}).get("name", "")
            ext_id = str(a.get("id", ""))
            existing = bookmark_crud.get_bookmark_by_musicbrainz_id(db, user_id, f"deezer:{ext_id}", "album") if ext_id else None
            items.append({
                "id": ext_id,
                "title": a.get("title"),
                "artist": artist,
                "date": a.get("release_date"),
                "status": None,
                "artwork_url": a.get("cover_medium") or a.get("cover") or a.get("cover_small"),
                "is_saved": existing is not None,
                "provider": "deezer",
                "item_type": "album",
            })
        return items, data.get("total", 0)
    return items, 0


@router.get("/album-detail", response_model=dict)
async def album_detail(
    provider: str = Query(..., description="musicbrainz | itunes | deezer"),
    album_id: str = Query(..., description="ID альбома в источнике"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    prov = provider.strip().lower()
    if prov not in ("musicbrainz", "itunes", "deezer"):
        raise HTTPException(status_code=400, detail="Unknown provider")

    # Saved state uses bookmarks table; for non-MB we encode provider prefix.
    bookmark_key = album_id if prov == "musicbrainz" else f"{prov}:{album_id}"
    existing = bookmark_crud.get_bookmark_by_musicbrainz_id(db, current_user.id, bookmark_key, "album")

    if prov == "musicbrainz":
        album = await MusicBrainzService.get_release_by_id(album_id)
        if not album:
            raise HTTPException(status_code=404, detail="Album not found")
        # Normalize tracks
        tracks = []
        for t in album.get("tracks", []) or []:
            tracks.append({
                "id": t.get("id"),
                "title": t.get("title"),
                "artist": None,
                "duration_ms": t.get("length"),
                "preview_url": None,
                "track_number": t.get("position"),
            })
        return {
            "id": album.get("id"),
            "title": album.get("title"),
            "artist": ", ".join([a.get("name") for a in album.get("artists", []) if a.get("name")]) or None,
            "artwork_url": None,
            "provider": "musicbrainz",
            "is_saved": existing is not None,
            "bookmark_key": bookmark_key,
            "tracks": tracks,
        }

    if prov == "itunes":
        data = await itunes_service.lookup_album(album_id)
        album = data.get("album")
        if not album:
            raise HTTPException(status_code=404, detail="Album not found")
        tracks = []
        for t in data.get("tracks", []):
            tracks.append({
                "id": str(t.get("trackId", "")),
                "title": t.get("trackName"),
                "artist": t.get("artistName"),
                "duration_ms": t.get("trackTimeMillis"),
                "preview_url": t.get("previewUrl"),
                "track_number": t.get("trackNumber"),
            })
        return {
            "id": str(album.get("collectionId", album_id)),
            "title": album.get("collectionName"),
            "artist": album.get("artistName"),
            "artwork_url": album.get("artworkUrl100") or album.get("artworkUrl60"),
            "provider": "itunes",
            "is_saved": existing is not None,
            "bookmark_key": bookmark_key,
            "tracks": tracks,
        }

    # Deezer
    data = await deezer_service.get_album(album_id)
    if not data:
        raise HTTPException(status_code=404, detail="Album not found")
    tracks = []
    for t in ((data.get("tracks") or {}).get("data") or []):
        tracks.append({
            "id": str(t.get("id", "")),
            "title": t.get("title"),
            "artist": (t.get("artist") or {}).get("name"),
            "duration_ms": (t.get("duration") or 0) * 1000 if t.get("duration") else None,
            "preview_url": t.get("preview"),
            "track_number": t.get("track_position"),
        })
    return {
        "id": str(data.get("id", album_id)),
        "title": data.get("title"),
        "artist": (data.get("artist") or {}).get("name"),
        "artwork_url": data.get("cover_medium") or data.get("cover") or data.get("cover_small"),
        "provider": "deezer",
        "is_saved": existing is not None,
        "bookmark_key": bookmark_key,
        "tracks": tracks,
    }


@router.get("/global", response_model=dict)
async def search_global(
    q: str = Query("", description="Поисковый запрос"),
    category: str = Query(..., description="Одна категория: songs, albums, artists"),
    provider: str = Query("musicbrainz", description="Источник: musicbrainz, itunes, deezer"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    user_id = getattr(current_user, "id", None)
    cat = category.strip().lower()
    prov = provider.strip().lower()
    if prov not in ("musicbrainz", "itunes", "deezer"):
        prov = "musicbrainz"
    logger.info("search_global: q=%r category=%r provider=%r skip=%s limit=%s", q, cat, prov, skip, limit)

    if not q or len(q.strip()) < 1:
        return {"items": [], "total": 0, "offset": skip, "provider": prov}

    # Песни — только внешние API (не БД)
    if cat == "songs":
        if prov == "musicbrainz":
            data = await MusicBrainzService.search_recording(query=q.strip(), limit=limit, offset=skip)
        elif prov == "itunes":
            data = await itunes_service.search(q.strip(), entity="song", limit=limit, offset=skip)
        else:
            data = await deezer_service.search_track(q.strip(), limit=limit, offset=skip)
        items, total = _normalize_songs(prov, data, cat)
        return {"items": items, "total": total, "offset": skip, "provider": prov}

    # Исполнители
    if cat == "artists":
        if prov == "musicbrainz":
            data = await MusicBrainzService.search_artist(query=q.strip(), limit=limit, offset=skip)
        elif prov == "itunes":
            data = await itunes_service.search(q.strip(), entity="musicArtist", limit=limit, offset=skip)
        else:
            data = await deezer_service.search_artist(q.strip(), limit=limit, offset=skip)
        items, total = _normalize_artists(prov, data, db, current_user.id)
        return {"items": items, "total": total, "offset": skip, "provider": prov}

    # Альбомы
    if cat == "albums":
        if prov == "musicbrainz":
            data = await MusicBrainzService.search_release(query=q.strip(), limit=limit, offset=skip)
        elif prov == "itunes":
            data = await itunes_service.search(q.strip(), entity="album", limit=limit, offset=skip)
        else:
            data = await deezer_service.search_album(q.strip(), limit=limit, offset=skip)
        items, total = _normalize_albums(prov, data, db, current_user.id)
        return {"items": items, "total": total, "offset": skip, "provider": prov}

    return {"items": [], "total": 0, "offset": skip, "provider": prov}

