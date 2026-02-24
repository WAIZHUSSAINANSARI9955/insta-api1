import asyncio
from app.services.scraper import InstagramScraper
import json

async def main():
    scraper = InstagramScraper()
    username = "rjamumtaz1"
    print(f"Testing scraper for: {username}")
    data = await scraper.scrape_profile(username)
    if data:
        print(f"SUCCESS! Found data for {username}")
        print(f"Followers: {data.get('followers_count')}")
        print(f"Media count: {len(data.get('media', []))}")
        if data.get('media'):
            print(f"First media URL: {data['media'][0]['media_url'][:50]}...")
    else:
        print(f"FAILED to scrape {username}")

if __name__ == "__main__":
    asyncio.run(main())
