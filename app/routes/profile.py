from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import logging
import traceback
from ..database import get_db
from ..models import User, Media
from ..schemas import UserResponse
from ..services.scraper import InstagramScraper

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["Profile"])
scraper = InstagramScraper()

@router.get("/{username}", response_model=UserResponse)
async def get_profile(username: str, force: bool = False, db: AsyncSession = Depends(get_db)):
    username = username.strip().lower().replace("@", "")
    logger.info(f"Targeting profile: {username} (Force: {force})")

    # 1. Check Cache
    try:
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.media))
        )
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Cache check failed: {e}")
        await db.rollback() # CRITICAL: Reset the transaction if it failed
        db_user = None

    current_time = datetime.utcnow()
    
    # Return cache if valid
    if db_user and not force:
        has_media = len(db_user.media) > 0
        is_fresh = db_user.last_scraped_at > current_time - timedelta(hours=6)
        has_counts = db_user.followers_count > 0
        
        if has_media and is_fresh and has_counts:
            logger.info(f"Returning cached data for {username}")
            return db_user
        
        # If no media but extremely recent (last 10 mins), don't hammer Instagram again
        # This prevents loop on private/empty accounts, but stays small enough for retries
        if not has_media and db_user.last_scraped_at > current_time - timedelta(minutes=10):
            logger.info(f"Returning recently attempted metadata for {username}")
            return db_user

    # 2. Scrape Fresh Data
    logger.info(f"Starting live scrape for: {username}")
    try:
        scraped_data = await scraper.scrape_profile(username)
        if not scraped_data:
            # If we fail, but have cache, return cache as fallback
            if db_user:
                logger.warning(f"Scrape failed for {username}, falling back to stale cache.")
                return db_user
            
            raise HTTPException(
                status_code=429, 
                detail="Instagram block or Rate Limit detected. Please wait 15-30 mins or provide a valid SESSION_ID."
            )

        # 3. Save to Database
        new_followers = scraped_data.get("follower_count", 0)
        new_following = scraped_data.get("following_count", 0)
        new_pic = scraped_data.get("profile_pic_url")
        new_bio = scraped_data.get("biography") or ""
        new_media_count = scraped_data.get("media_count", 0)

        if db_user:
            # Update, but preserve good data if new scrape couldn't get it (IP blocked = 0 counts)
            db_user.full_name = scraped_data.get("full_name") or db_user.full_name or username
            db_user.profile_pic = new_pic or db_user.profile_pic  # Keep old pic if new is null
            db_user.followers_count = new_followers if new_followers > 0 else db_user.followers_count
            db_user.following_count = new_following if new_following > 0 else db_user.following_count
            db_user.posts_count = new_media_count if new_media_count > 0 else db_user.posts_count
            db_user.biography = new_bio if new_bio else db_user.biography
            db_user.last_scraped_at = current_time
            # Delete old media before adding new
            await db.execute(delete(Media).where(Media.user_id == db_user.id))
        else:
            # Create new
            db_user = User(
                username=scraped_data.get("username") or username,
                full_name=scraped_data.get("full_name") or username,
                profile_pic=new_pic,
                followers_count=new_followers,
                following_count=new_following,
                posts_count=new_media_count,
                biography=new_bio,
                last_scraped_at=current_time
            )
            db.add(db_user)
            await db.flush()

        # Add media
        for m in scraped_data.get("media", []):
            try:
                # Safe date parsing
                ts = m.get("created_at")
                dt = current_time
                if ts and isinstance(ts, (int, float)):
                    dt = datetime.fromtimestamp(ts)
                elif ts and str(ts).isdigit():
                    dt = datetime.fromtimestamp(int(ts))
                
                new_m = Media(
                    user_id=db_user.id,
                    media_type=m["media_type"],
                    media_url=m["media_url"],
                    thumbnail_url=m.get("thumbnail_url"),
                    caption=m.get("caption", ""),
                    created_at=dt
                )
                db.add(new_m)
            except Exception as me:
                logger.warning(f"Could not parse media item: {me}")

        try:
            await db.commit()
        except Exception as commit_error:
            await db.rollback()
            logger.error(f"Commit failed: {commit_error}")
            raise HTTPException(status_code=500, detail=f"Database commit failed: {str(commit_error)}")
        
        # Final fetch to ensure all data is loaded correctly for response
        try:
            final_stmt = (
                select(User)
                .where(User.id == db_user.id)
                .options(selectinload(User.media))
            )
            final_result = await db.execute(final_stmt)
            return final_result.scalar_one()
        except Exception as final_fetch_error:
            logger.error(f"Final fetch failed: {final_fetch_error}")
            # If everything else succeeded, we might just return the object we have
            return db_user

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"CRITICAL ERROR in get_profile: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Backend Error: {str(e)}. Check server logs for details."
        )
