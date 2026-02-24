import httpx
import asyncio
import zipfile
import io
from typing import List, Tuple, Optional
from fastapi.responses import StreamingResponse

class DownloaderService:
    async def download_file(self, client: httpx.AsyncClient, url: str) -> Optional[bytes]:
        try:
            # Use browser-like headers for CDN downloads
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Origin": "https://www.instagram.com",
                "Referer": "https://www.instagram.com/",
            }
            response = await client.get(url, timeout=30.0, headers=headers)
            if response.status_code == 200:
                return response.content
            print(f"DEBUG: CDN download failed for {url[:50]}... Status: {response.status_code}")
        except Exception as e:
            print(f"Error downloading {url[:50]}...: {e}")
        return None

    async def create_bulk_zip(self, media_urls: List[str], username: str):
        zip_buffer = io.BytesIO()
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            tasks = [self.download_file(client, url) for url in media_urls]
            files_content = await asyncio.gather(*tasks)

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for i, content in enumerate(files_content):
                    if content:
                        url = media_urls[i].lower()
                        # Better extension detection
                        ext = "mp4" if ".mp4" in url or "video" in url else "jpg"
                        
                        filename = f"{username}_{i+1}.{ext}"
                        zip_file.writestr(filename, content)

        zip_buffer.seek(0)
        return zip_buffer

    async def get_zip_stream(self, media_urls: List[str], username: str):
        zip_buffer = await self.create_bulk_zip(media_urls, username)
        return zip_buffer
