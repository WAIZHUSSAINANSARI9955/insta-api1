import asyncio
import httpx
from bs4 import BeautifulSoup

async def check():
    url = "https://www.instagram.com/devil_heart.47/"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=10.0) as client:
        try:
            r = await client.get(url)
            print(f"Status: {r.status_code}")
            print(f"URL: {r.url}")
            if "login" in str(r.url):
                print("REDIRECTED TO LOGIN")
            else:
                soup = BeautifulSoup(r.content, "lxml")
                title = soup.find("title")
                print(f"Title: {title.text if title else 'No Title'}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
