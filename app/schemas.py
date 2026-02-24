from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class MediaBase(BaseModel):
    media_type: str
    video_url: str = Field(..., alias="media_url", serialization_alias="video_url", validation_alias="media_url")
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    is_video: bool = True
    shortcode: Optional[str] = ""

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
    profile_pic_url: Optional[str] = Field(None, alias="profile_pic_url", serialization_alias="profile_pic_url", validation_alias="profile_pic")
    follower_count: int = Field(0, alias="follower_count", serialization_alias="follower_count", validation_alias="followers_count")
    following_count: int = 0
    media_count: int = Field(0, alias="media_count", serialization_alias="media_count", validation_alias="posts_count")
    biography: Optional[str] = ""

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
