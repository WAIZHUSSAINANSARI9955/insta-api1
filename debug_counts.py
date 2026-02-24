import asyncio
import os
import json
from dotenv import load_dotenv
from app.services.scraper import InstagramScraper

load_dotenv()

async def debug_scrape():
    s = InstagramScraper()
    username = "explainzwar"
    print(f"Scraping {username}...")
    data = await s.scrape_profile(username)
    if data:
        # Hide long URLs for readability
        debug_data = data.copy()
        debug_data['profile_pic_url'] = (data['profile_pic_url'][:50] + "...") if data.get('profile_pic_url') else None
        debug_data['media'] = f"[{len(data['media'])} items found]"
        print(json.dumps(debug_data, indent=2))
        
        # Check first media item for detail
        if data['media']:
             print("\nFirst Media Item Sample:")
             sample = data['media'][0].copy()
             sample['media_url'] = sample['media_url'][:50] + "..."
             sample['thumbnail_url'] = sample['thumbnail_url'][:50] + "..."
             print(json.dumps(sample, indent=2))
    else:
        print("FAILED to scrape.")

if __name__ == "__main__":
    asyncio.run(debug_scrape())
