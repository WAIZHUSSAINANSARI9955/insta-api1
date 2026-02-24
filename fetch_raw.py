import httpx
import asyncio

async def fetch_and_save(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "ig_did=D7E8; mid=Y1; csrftoken=val; datr=foo;",
        "X-IG-App-ID": "936619743392459"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        with open(f"raw_{username}.html", "wb") as f:
            f.write(response.content)
        print(f"Saved to raw_{username}.html, size: {len(response.content)}")

if __name__ == "__main__":
    asyncio.run(fetch_and_save("rjamumtaz1"))
