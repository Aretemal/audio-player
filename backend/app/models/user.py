from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    theme = Column(String(10), default="light", nullable=False)

    songs = relationship("Song", secondary="user_song", back_populates="users")
    albums = relationship("Album", secondary="user_album", back_populates="users")
    playlists = relationship("Playlist", secondary="user_playlist", back_populates="users")
    bookmarks = relationship("Bookmark", back_populates="user")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

