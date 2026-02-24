import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_session():
    sid = os.getenv("INSTAGRAM_SESSION_ID")
    print(f"Testing Session ID: {sid[:20]}...")
    
    # We use the most basic endpoint that requires login
    url = "https://www.instagram.com/api/v1/users/web_profile_info/?username=instagram"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "Cookie": f"sessionid={sid};",
        "X-ASBD-ID": "129477",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            r = await client.get(url)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print("✅ SESSION IS VALID!")
            elif r.status_code == 429:
                print("❌ RATE LIMITED (429) - Your IP is temporarily banned by Instagram.")
            elif r.status_code == 401:
                print("❌ SESSION EXPIRED - You need to get a new sessionid from your browser.")
            else:
                print(f"❌ FAILED with status {r.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_session())
