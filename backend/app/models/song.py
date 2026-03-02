from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, Table, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.models.base import Base

user_song_association = Table(
    'user_song',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True)
)


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=True)
    artist = Column(String(255), nullable=True)
    src = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)

    album_id = Column(Integer, ForeignKey('albums.id'), nullable=True)
    album = relationship("Album", back_populates="songs")

    users = relationship("User", secondary=user_song_association, back_populates="songs")
    playlists = relationship("Playlist", secondary="playlist_song", back_populates="songs")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

