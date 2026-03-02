import uuid
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_from_request, verify_auth_global
from app.core.config import settings
from app.crud import song as song_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.song import SongRead, SongUpdate

router = APIRouter(
    prefix="/songs",
    tags=["songs"],
    dependencies=[Depends(verify_auth_global)],
)

ALLOWED_PREVIEW_HOSTS = ("itunes.apple.com", "cdn.apple.com", "dzcdn.net", "cdnt-preview.dzcdn.net")


class FromPreviewRequest(BaseModel):
    preview_url: str
    title: str
    artist: str
    album: Optional[str] = None


@router.get("/", response_model=list[SongRead])
def list_songs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    songs = song_crud.get_songs_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    
    result = []
    for song in songs:
        album_name = song.album.title if song.album else None
        song_dict = {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "src": song.src,
            "album": album_name,
            "file_size": song.file_size,
            "user_ids": [user.id for user in song.users],
            "created_at": song.created_at,
            "updated_at": song.updated_at,
        }
        result.append(SongRead(**song_dict))
    return result


@router.post("/", response_model=SongRead, status_code=status.HTTP_201_CREATED)
def create_song(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    artist: Optional[str] = Form(None),
    album: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file"
        )
    
    song = song_crud.create_song(
        db=db,
        file=file,
        user=current_user,
        title=title,
        artist=artist,
        album=album,
    )
    
    album_name = song.album.title if song.album else None
    return SongRead(
        id=song.id,
        title=song.title,
        artist=song.artist,
        src=song.src,
        album=album_name,
        file_size=song.file_size,
        user_ids=[user.id for user in song.users],
        created_at=song.created_at,
        updated_at=song.updated_at,
    )

@router.post("/{song_id}/add-to-library", status_code=status.HTTP_200_OK)
def add_song_to_library(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    result = song_crud.add_song_to_user(db, user_id=current_user.id, song_id=song_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    if result is False:
        return {"detail": "Already in your library", "added": False}
    return {"detail": "Added to your library", "added": True}


@router.delete("/{song_id}/add-to-library", status_code=status.HTTP_200_OK)
def remove_song_from_library(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    result = song_crud.remove_song_from_user(db, user_id=current_user.id, song_id=song_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    if result is False:
        return {"detail": "Was not in your library", "removed": False}
    return {"detail": "Removed from your library", "removed": True}


def _is_allowed_preview_url(url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        return any(host == h or host.endswith("." + h) for h in ALLOWED_PREVIEW_HOSTS)
    except Exception:
        return False


@router.post("/from-preview", response_model=SongRead, status_code=status.HTTP_201_CREATED)
async def create_song_from_preview(
    body: FromPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    if not _is_allowed_preview_url(body.preview_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Preview URL not allowed")
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = ".m4a" if "apple.com" in body.preview_url else ".mp3"
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_filename
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(body.preview_url)
            resp.raise_for_status()
            file_path.write_bytes(resp.content)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Failed to fetch preview: {e}")
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    song = song_crud.create_song_from_path(
        db, file_path, current_user,
        title=body.title or "Unknown",
        artist=body.artist or "Unknown",
        album=body.album,
    )
    album_name = song.album.title if song.album else None
    return SongRead(
        id=song.id,
        title=song.title,
        artist=song.artist,
        src=song.src,
        album=album_name,
        file_size=song.file_size,
        user_ids=[u.id for u in song.users],
        created_at=song.created_at,
        updated_at=song.updated_at,
    )


@router.get("/download-external")
async def download_external(
    url: str = "",
    current_user: User = Depends(get_user_from_request),
):
    if not _is_allowed_preview_url(url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL not allowed")
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Failed to fetch: {e}")
    filename = "preview.mp3"
    if "apple.com" in url:
        filename = "preview.m4a"
    return Response(
        content=content,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/album/{album_id}", response_model=list[SongRead])
def get_songs_by_album(
    album_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    songs = song_crud.get_songs_by_album(db, album_id)
    result = []
    for song in songs:
        album_name = song.album.title if song.album else None
        result.append(SongRead(
            id=song.id, 
            title=song.title, 
            artist=song.artist, 
            src=song.src,
            album=album_name,
            file_size=song.file_size,
            user_ids=[user.id for user in song.users], 
            created_at=song.created_at, 
            updated_at=song.updated_at
        ))
    return result


@router.get("/{song_id}/download")
def download_song(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    song = song_crud.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    if current_user not in song.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    file_path = Path(settings.UPLOAD_DIR) / song.src
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    filename = (song.title or "song").strip() or "song"
    safe = "".join(c for c in filename if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
    if not safe:
        safe = "song"
    ext = file_path.suffix or ".mp3"
    return FileResponse(
        path=str(file_path),
        media_type="application/octet-stream",
        filename=f"{safe}{ext}",
    )


@router.get("/{song_id}/stream")
async def stream_song(
    song_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    song = song_crud.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

    if current_user not in song.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    file_path = Path(settings.UPLOAD_DIR) / song.src
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    file_size = file_path.stat().st_size
    range_header = request.headers.get("range")
    
    if range_header:
        range_match = range_header.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        end = min(end, file_size - 1)
        content_length = end - start + 1

        def iterfile():
            with open(file_path, "rb") as file:
                file.seek(start)
                remaining = content_length
                while remaining:
                    chunk_size = min(8192, remaining)
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        content_type = "audio/mpeg"
        if song.src.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif song.src.endswith(".wav"):
            content_type = "audio/wav"
        elif song.src.endswith(".ogg"):
            content_type = "audio/ogg"
        elif song.src.endswith(".m4a"):
            content_type = "audio/mp4"

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": content_type,
        }
        
        return StreamingResponse(
            iterfile(),
            status_code=206,
            headers=headers,
            media_type=content_type,
        )
    else:
        def iterfile():
            with open(file_path, "rb") as file:
                while True:
                    chunk = file.read(8192)
                    if not chunk:
                        break
                    yield chunk

        content_type = "audio/mpeg"
        if song.src.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif song.src.endswith(".wav"):
            content_type = "audio/wav"
        elif song.src.endswith(".ogg"):
            content_type = "audio/ogg"
        elif song.src.endswith(".m4a"):
            content_type = "audio/mp4"
        
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": content_type,
        }
        
        return StreamingResponse(
            iterfile(),
            status_code=200,
            headers=headers,
            media_type=content_type,
        )
