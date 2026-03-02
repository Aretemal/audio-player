from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class SongBase(BaseModel):
    src: str


class SongCreate(BaseModel):
    title: Optional[str] = None
    src: str


class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None


class SongRead(BaseModel):
    id: int
    title: Optional[str] = None
    artist: Optional[str] = None
    src: str
    album: Optional[str] = None
    file_size: Optional[int] = None
    user_ids: List[int] = [] 

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

