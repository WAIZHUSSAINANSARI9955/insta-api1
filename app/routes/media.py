import httpx
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

@router.get("/proxy")
async def proxy_media(url: str):
    """
    Proxies media requests to bypass CORS and 403 errors from Instagram's CDN.
    Use in frontend as: http://127.0.0.1:8000/proxy?url=BASE64_OR_ENCODED_URL
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
        
    async def stream_media():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Referer": "https://www.instagram.com/",
            "Accept": "*/*",
        }
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
            try:
                async with client.stream("GET", url) as response:
                    if response.status_code != 200:
                        raise HTTPException(status_code=response.status_code, detail="Failed to fetch media from source")
                    
                    content_type = response.headers.get("content-type", "application/octet-stream")
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

    return StreamingResponse(stream_media())

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
