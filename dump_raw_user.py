import httpx
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def dump_raw():
    sid = os.getenv("INSTAGRAM_SESSION_ID")
    username = "explainzwar"
    url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/",
        "Cookie": f"sessionid={sid};"
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        r = await client.get(url)
        if r.status_code == 200:
            data = r.json()
            # Only dump the user part
            user = data.get("user", {})
            print(json.dumps(user, indent=2))
        else:
            print(f"Error: {r.status_code}")

if __name__ == "__main__":
    asyncio.run(dump_raw())
