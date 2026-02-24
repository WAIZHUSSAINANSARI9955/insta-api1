import httpx
import asyncio
import os
import random
from dotenv import load_dotenv

load_dotenv()

async def super_check():
    sid = os.getenv("INSTAGRAM_SESSION_ID")
    # Using the mobile-specific API endpoint
    url = "https://i.instagram.com/api/v1/users/web_profile_info/?username=realumairr"
    
    headers = {
        "User-Agent": "Instagram 219.0.0.12.117 Android",
        "X-IG-App-ID": "936619743392459",
        "X-IG-WWW-Claim": "0",
        "X-ASBD-ID": "129477",
        "Cookie": f"sessionid={sid};",
        "Accept-Language": "en-US",
        "Connection": "keep-alive",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # Long delay to bypass current block
        print("Waiting 5 seconds for safety...")
        await asyncio.sleep(5)
        
        try:
            r = await client.get(url)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print("SUCCESS: We broke through the block!")
                data = r.json()
                print(f"Profile: {data.get('data', {}).get('user', {}).get('full_name')}")
            elif r.status_code == 429:
                print("FAILED: IP is still Rate Limited. Please wait 15 minutes.")
            else:
                print(f"FAILED: Status {r.status_code}. Instagram is being tough.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(super_check())
