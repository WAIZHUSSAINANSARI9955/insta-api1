from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from ..database import get_db
from ..models import User, Media
from ..schemas import UserResponse
from ..services.scraper import InstagramScraper

router = APIRouter(prefix="/profile", tags=["Profile"])
scraper = InstagramScraper()

@router.get("/{username}", response_model=UserResponse)
async def get_profile(username: str, db: AsyncSession = Depends(get_db)):
    # 1. Check if user exists in DB
    result = await db.execute(select(User).where(User.username == username))
    db_user = result.scalar_one_or_none()
    
    current_time = datetime.utcnow()
    
    # 2. Check if cache is valid (6 hours)
    if db_user and db_user.last_scraped_at > current_time - timedelta(hours=6):
        # Fetch related media for the response
        media_result = await db.execute(select(Media).where(Media.user_id == db_user.id))
        db_user.media = media_result.scalars().all()
        return db_user

    # 3. Scrape fresh data
    try:
        scraped_data = await scraper.scrape_profile(username)
        if not scraped_data:
            raise HTTPException(status_code=404, detail="Profile not found or could not be scraped")
        
        if db_user:
            # Update existing user
            db_user.full_name = scraped_data["full_name"]
            db_user.profile_pic = scraped_data["profile_pic"]
            db_user.followers_count = scraped_data["followers_count"]
            db_user.following_count = scraped_data["following_count"]
            db_user.posts_count = scraped_data["posts_count"]
            db_user.last_scraped_at = current_time
            
            # Clear old media and add new one
            # For simplicity, we delete all and re-add. 
            # In a production app, you might want to sync instead.
            from sqlalchemy import delete
            await db.execute(delete(Media).where(Media.user_id == db_user.id))
        else:
            # Create new user
            db_user = User(
                username=scraped_data["username"],
                full_name=scraped_data["full_name"],
                profile_pic=scraped_data["profile_pic"],
                followers_count=scraped_data["followers_count"],
                following_count=scraped_data["following_count"],
                posts_count=scraped_data["posts_count"],
                last_scraped_at=current_time
            )
            db.add(db_user)
            await db.flush() # To get the ID
        
        # Add media
        new_media = []
        for m in scraped_data["media"]:
            media_obj = Media(
                user_id=db_user.id,
                media_type=m["media_type"],
                media_url=m["media_url"],
                thumbnail_url=m["thumbnail_url"],
                caption=m["caption"],
                created_at=datetime.fromtimestamp(m["created_at"]) if m["created_at"] else current_time
            )
            new_media.append(media_obj)
        
        db.add_all(new_media)
        await db.commit()
        
        # Refresh and return
        db_user.media = new_media
        return db_user

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")
