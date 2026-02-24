import asyncio
import httpx
import json

async def test_api(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                user = data.get("data", {}).get("user", {})
                if user:
                    print(f"Username: {user.get('username')}")
                    media = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
                    print(f"Media Count: {len(media)}")
                    if len(media) > 0:
                        print("SUCCESS: Found media via API!")
                else:
                    print("Could not find user in API response")
            else:
                print(f"API Failed: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api("devil_heart.47"))
