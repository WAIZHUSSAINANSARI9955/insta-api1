import asyncio
import httpx
from bs4 import BeautifulSoup
import re

async def test_scrape(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        soup = BeautifulSoup(response.content, "lxml")
        title = soup.find("title")
        if title:
            print(f"Title: {title.text}")
        
        description_tag = soup.find("meta", property="og:description")
        if description_tag:
             print(f"Description: {description_tag['content']}")

if __name__ == "__main__":
    asyncio.run(test_scrape("sana.zulfiqar5"))
