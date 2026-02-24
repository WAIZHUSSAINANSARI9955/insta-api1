import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_mobile_api():
    sid = os.getenv("INSTAGRAM_SESSION_ID")
    # Mobile endpoint
    url = "https://i.instagram.com/api/v1/users/web_profile_info/?username=instagram"
    
    headers = {
        "User-Agent": "Instagram 219.0.0.12.117 Android (30/11; 480dpi; 1080x2186; vivo; V2031; V2031; qcom; en_US; 332152841)",
        "X-IG-App-ID": "1217981644879628", # Mobile App ID
        "Cookie": f"sessionid={sid};",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            r = await client.get(url)
            print(f"Mobile API Status: {r.status_code}")
            if r.status_code == 200:
                print("✅ MOBILE API WORKED!")
            else:
                print(f"❌ MOBILE API FAILED: {r.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mobile_api())
