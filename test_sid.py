import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_session():
    sid = os.getenv("INSTAGRAM_SESSION_ID")
    url = "https://www.instagram.com/api/v1/users/web_profile_info/?username=anshul.tweaks"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "Cookie": f"sessionid={sid};",
        "X-ASBD-ID": "129477",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        r = await client.get(url)
        print(f"Status: {r.status_code}")
        # print(r.text[:500])
        if r.status_code == 200:
            print("SUCCESS: Session ID is valid and working!")
            data = r.json()
            print(f"Found User: {data.get('data', {}).get('user', {}).get('full_name')}")
        else:
            print(f"FAILED: Status {r.status_code}")
            if "login" in r.text: print("Reason: Redirected to login")

if __name__ == "__main__":
    asyncio.run(test_session())
