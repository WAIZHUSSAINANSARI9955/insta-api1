from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..models import User, Media, Download
from ..schemas import MediaResponse
from ..services.downloader import DownloaderService

router = APIRouter(tags=["Media"])
downloader = DownloaderService()

@router.get("/media/{username}", response_model=List[MediaResponse])
async def get_user_media(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found in database. Please fetch profile first.")
    
    media_result = await db.execute(select(Media).where(Media.user_id == user.id))
    return media_result.scalars().all()

@router.post("/bulk-download/{username}")
async def bulk_download(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Fetch profile first.")
    
    media_result = await db.execute(select(Media).where(Media.user_id == user.id))
    media_items = media_result.scalars().all()
    
    if not media_items:
        raise HTTPException(status_code=404, detail="No media found for this user.")
    
    urls = [m.media_url for m in media_items]
    
    # Track download
    download_record = Download(user_id=user.id, download_type="bulk")
    db.add(download_record)
    await db.commit()
    
    zip_buffer = await downloader.get_zip_stream(urls, username)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={username}_bulk_download.zip"}
    )
