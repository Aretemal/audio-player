from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.playlist import Playlist
from app.models.song import Song
from app.models.user import User
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate


def get_playlist(db: Session, playlist_id: int) -> Optional[Playlist]:
    return db.query(Playlist).filter(Playlist.id == playlist_id).first()


def get_playlists(db: Session, skip: int = 0, limit: int = 100) -> List[Playlist]:
    return db.query(Playlist).offset(skip).limit(limit).all()


def get_playlists_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Playlist]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    return user.playlists[skip:skip + limit] if user.playlists else []


def create_playlist(db: Session, playlist_in: PlaylistCreate, user_id: int) -> Playlist:
    playlist_data = playlist_in.model_dump(exclude={"song_ids"})
    
    db_playlist = Playlist(**playlist_data)
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db_playlist.users.append(user)
    
    db.add(db_playlist)
    db.flush()
    
    if playlist_in.song_ids:
        songs = db.query(Song).filter(Song.id.in_(playlist_in.song_ids)).all()
        for song in songs:
            db_playlist.songs.append(song)
    
    db.commit()
    db.refresh(db_playlist)
    
    return db_playlist


def update_playlist(db: Session, db_playlist: Playlist, playlist_in: PlaylistUpdate) -> Playlist:
    data = playlist_in.model_dump(exclude_unset=True, exclude={"song_ids"})
    
    for field, value in data.items():
        setattr(db_playlist, field, value)
    
    if playlist_in.song_ids is not None:
        db_playlist.songs.clear()
        if playlist_in.song_ids:
            songs = db.query(Song).filter(Song.id.in_(playlist_in.song_ids)).all()
            for song in songs:
                db_playlist.songs.append(song)
    
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


def delete_playlist(db: Session, db_playlist: Playlist) -> None:
    db.delete(db_playlist)
    db.commit()

