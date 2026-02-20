from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class MediaBase(BaseModel):
    media_type: str
    media_url: str
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None

class MediaCreate(MediaBase):
    user_id: UUID

class MediaResponse(MediaBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    profile_pic: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID
    last_scraped_at: datetime
    media: List[MediaResponse] = []

    class Config:
        from_attributes = True

class DownloadBase(BaseModel):
    download_type: str

class DownloadCreate(DownloadBase):
    user_id: UUID

class DownloadResponse(DownloadBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
