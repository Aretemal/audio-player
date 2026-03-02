from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class PlaylistBase(BaseModel):
    title: str
    description: Optional[str] = None


class PlaylistCreate(BaseModel):
    title: str
    description: Optional[str] = None
    song_ids: List[int] = []


class PlaylistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    song_ids: Optional[List[int]] = None


class PlaylistRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    song_ids: Optional[List[int]] = None
    user_ids: Optional[List[int]] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

