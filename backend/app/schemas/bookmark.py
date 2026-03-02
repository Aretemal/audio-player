from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class BookmarkCategoryBase(BaseModel):
    name: str


class BookmarkCategoryCreate(BookmarkCategoryBase):
    pass


class BookmarkCategoryRead(BookmarkCategoryBase):
    id: int
    is_default: bool
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookmarkBase(BaseModel):
    bookmark_type: str
    musicbrainz_id: str
    title: str
    extra_data: Optional[str] = None


class BookmarkCreate(BookmarkBase):
    category_ids: Optional[List[int]] = None


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    extra_data: Optional[str] = None
    category_ids: Optional[List[int]] = None


class BookmarkRead(BookmarkBase):
    id: int
    user_id: int
    categories: List[BookmarkCategoryRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
