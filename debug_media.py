import asyncio
import httpx
from bs4 import BeautifulSoup
import json
import re

async def debug_media(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        
        with open("raw_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        soup = BeautifulSoup(response.content, "lxml")
        scripts = soup.find_all("script")
        
        found_json = False
        for script in scripts:
            content = script.string or ""
            if '"edge_owner_to_timeline_media"' in content:
                found_json = True
                print("FOUND edge_owner_to_timeline_media in a script!")
                # Get a snippet
                idx = content.find('"edge_owner_to_timeline_media"')
                print(f"Snippet: {content[idx:idx+200]}")
        
        if not found_json:
            print("COULD NOT FIND edge_owner_to_timeline_media IN ANY SCRIPT TAG")
            
if __name__ == "__main__":
    asyncio.run(debug_media("devil_heart.47"))
