import asyncio
import os
import json
from app.services.scraper import InstagramScraper
from dotenv import load_dotenv

load_dotenv()

async def test_counts():
    scraper = InstagramScraper()
    # Username to test - you can change this
    test_username = "jerry94196" 
    
    print(f"--- Testing counts for @{test_username} ---")
    
    # We call the scraper directly to see what it returns
    result = await scraper.scrape_profile(test_username)
    
    if result:
        print("\n=== SUCCESS ===")
        print(f"Username: {result.get('username')}")
        print(f"Full Name: {result.get('full_name')}")
        print(f"Followers: {result.get('follower_count')}")
        print(f"Following: {result.get('following_count')}")
        print(f"Biography: {result.get('biography')}")
        print(f"Media Count (Items): {len(result.get('media', []))}")
        
        if result.get('follower_count', 0) > 0:
            print("\n✅ Follower count is successfully fetched!")
        else:
            print("\n❌ Follower count is still 0. Possible block or masking.")
            
        if result.get('biography'):
            print("✅ Biography is successfully fetched!")
        else:
            print("⚠️ Biography is empty.")
    else:
        print("\n❌ Scrape failed entirely.")

if __name__ == "__main__":
    asyncio.run(test_counts())
