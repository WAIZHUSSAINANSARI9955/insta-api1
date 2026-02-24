import httpx
import asyncio

async def fetch_and_save(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        with open(f"raw_googlebot_{username}.html", "wb") as f:
            f.write(response.content)
        print(f"Saved to raw_googlebot_{username}.html, size: {len(response.content)}")
        if b"Followers" in response.content:
            print("SUCCESS: Found 'Followers' in content!")
        else:
            print("FAILED: No 'Followers' found (probably login wall)")

if __name__ == "__main__":
    asyncio.run(fetch_and_save("rjamumtaz1"))
