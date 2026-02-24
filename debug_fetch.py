import httpx
import asyncio
from bs4 import BeautifulSoup
import re

async def debug_html(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "X-IG-App-ID": "936619743392459",
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        r = await client.get(url)
        print(f"Status: {r.status_code}")
        open("debug_output.html", "wb").write(r.content)
        print(f"Content length: {len(r.content)}")
        if b"login" in r.content.lower():
            print("DETECTED: Login wall")
        if b"checkpoint" in r.content.lower():
            print("DETECTED: Checkpoint/Block")

if __name__ == "__main__":
    asyncio.run(debug_html("rjamumtaz1"))
