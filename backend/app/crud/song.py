import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.song import Song
from app.models.user import User
from app.schemas.song import SongCreate, SongUpdate


def get_songs(db: Session, skip: int = 0, limit: int = 100) -> List[Song]:
    return db.query(Song).offset(skip).limit(limit).all()


def get_songs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Song]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
        
    return user.songs[skip:skip + limit] if user.songs else []


def save_uploaded_file(file: UploadFile, upload_dir: Path) -> str:
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / unique_filename
    
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return unique_filename


def create_song(
    db: Session,
    file: UploadFile,
    user: User,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
) -> Song:
    from app.crud import album as album_crud
    from app.schemas.album import AlbumCreate
    
    upload_dir = Path(settings.UPLOAD_DIR)
    
    file_path = save_uploaded_file(file, upload_dir)
    saved_file_path = upload_dir / file_path
    file_size = saved_file_path.stat().st_size if saved_file_path.exists() else None
    album_id = None
    if album:
        existing_albums = album_crud.get_albums_by_user(db, user_id=user.id)
        existing_album = next((a for a in existing_albums if a.title == album), None)
        
        if existing_album:
            album_id = existing_album.id
        else:
            album_data = AlbumCreate(title=album, creator=artist, song_ids=[])
            new_album = album_crud.create_album(db, album_data, user_id=user.id)
            album_id = new_album.id
    
    db_song = Song(
        src=file_path,
        title=title,
        artist=artist,
        album_id=album_id,
        file_size=file_size,
    )
    
    db_song.users.append(user)
    
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    
    return db_song

def create_song_from_path(
    db: Session,
    file_path: Path,
    user: User,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
) -> Song:
    """Создать песню из уже сохранённого файла (например, скачанного по URL)."""
    from app.crud import album as album_crud
    from app.schemas.album import AlbumCreate

    upload_dir = Path(settings.UPLOAD_DIR)
    unique_filename = file_path.name
    file_size = file_path.stat().st_size if file_path.exists() else None
    album_id = None
    if album:
        existing_albums = album_crud.get_albums_by_user(db, user_id=user.id)
        existing_album = next((a for a in existing_albums if a.title == album), None)
        if existing_album:
            album_id = existing_album.id
        else:
            album_data = AlbumCreate(title=album, creator=artist, song_ids=[])
            new_album = album_crud.create_album(db, album_data, user_id=user.id)
            album_id = new_album.id

    db_song = Song(
        src=unique_filename,
        title=title,
        artist=artist,
        album_id=album_id,
        file_size=file_size,
    )
    db_song.users.append(user)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def get_song(db: Session, song_id: int) -> Optional[Song]:
    return db.query(Song).filter(Song.id == song_id).first()


def add_song_to_user(db: Session, user_id: int, song_id: int) -> Optional[bool]:
    """Добавить песню в коллекцию пользователя. Возвращает True если добавлено, False если уже было, None если песня не найдена."""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if user in song.users:
        return False
    song.users.append(user)
    db.commit()
    return True


def remove_song_from_user(db: Session, user_id: int, song_id: int) -> Optional[bool]:
    """Убрать песню из коллекции пользователя. Возвращает True если убрано, False если не было, None если песня не найдена."""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if user not in song.users:
        return False
    song.users.remove(user)
    db.commit()
    return True


def get_songs_by_album(db: Session, album_id: int) -> List[Song]:
    return db.query(Song).filter(Song.album_id == album_id).all()