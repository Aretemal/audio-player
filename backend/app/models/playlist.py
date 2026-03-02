from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base

user_playlist_association = Table(
    'user_playlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True)
)

playlist_song_association = Table(
    'playlist_song',
    Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True)
)


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    songs = relationship("Song", secondary=playlist_song_association, back_populates="playlists")
    users = relationship("User", secondary=user_playlist_association, back_populates="playlists")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

