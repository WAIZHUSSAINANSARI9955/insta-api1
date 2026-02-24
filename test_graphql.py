import httpx
import asyncio
import json

async def test_graphql(username):
    # 1. Get User ID first
    url_id = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        # Try to get the initial page to get a cookie
        await client.get(f"https://www.instagram.com/{username}/")
        
        # Now try the API
        response = await client.get(url_id)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Found data via GraphQL!")
            data = response.json()
            user = data.get("data", {}).get("user", {})
            print(f"Posts: {user.get('edge_owner_to_timeline_media', {}).get('count')}")
        else:
            print(f"Failed: {response.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_graphql("rjamumtaz1"))
