import asyncio
import httpx
import json

async def test_api_scrape(username):
    # Modern Instagram Web API endpoint
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "X-IG-App-ID": "936619743392459", # Common Web App ID
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                user = data.get("data", {}).get("user", {})
                if user:
                    print(f"Found User: {user.get('full_name')}")
                    print(f"Followers: {user.get('edge_followed_by', {}).get('count')}")
                    media_count = user.get('edge_owner_to_timeline_media', {}).get('count')
                    print(f"Media Count: {media_count}")
                    
                    edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
                    print(f"Fetched {len(edges)} media items")
                else:
                    print("User data not found in JSON response")
            except Exception as e:
                print(f"JSON Parse Error: {e}")
                print(response.text[:500])
        else:
            print(f"Response Text: {response.text[:500]}")

if __name__ == "__main__":
    asyncio.run(test_api_scrape("sana.zulfiqar5"))
