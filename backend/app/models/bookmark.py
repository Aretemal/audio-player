from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base

bookmark_category_association = Table(
    'bookmark_category',
    Base.metadata,
    Column('bookmark_id', Integer, ForeignKey('bookmarks.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('bookmark_categories.id'), primary_key=True)
)


class BookmarkCategory(Base):
    """Категория закладок (общая или кастомная)"""
    __tablename__ = "bookmark_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    bookmarks = relationship("Bookmark", secondary=bookmark_category_association, back_populates="categories")


class Bookmark(Base):
    """Закладка на исполнителя или альбом"""
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bookmark_type = Column(String(20), nullable=False)
    musicbrainz_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    extra_data = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="bookmarks")
    categories = relationship("BookmarkCategory", secondary=bookmark_category_association, back_populates="bookmarks")
