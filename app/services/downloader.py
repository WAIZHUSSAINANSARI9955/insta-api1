import httpx
import asyncio
import zipfile
import io
from typing import List, Tuple, Optional
from fastapi.responses import StreamingResponse

class DownloaderService:
    async def download_file(self, client: httpx.AsyncClient, url: str) -> Optional[bytes]:
        try:
            response = await client.get(url, timeout=30.0)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Error downloading {url}: {e}")
        return None

    async def create_bulk_zip(self, media_urls: List[str], username: str):
        # We'll use a BytesIO buffer to store the ZIP
        zip_buffer = io.BytesIO()
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            tasks = [self.download_file(client, url) for url in media_urls]
            files_content = await asyncio.gather(*tasks)

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for i, content in enumerate(files_content):
                    if content:
                        # Determine extension from URL or default to jpg
                        ext = "mp4" if "video" in media_urls[i] or "reel" in media_urls[i] else "jpg"
                        # This logic is simplified; in a real app, you'd check headers or actual content type
                        filename = f"{username}_{i+1}.{ext}"
                        zip_file.writestr(filename, content)

        zip_buffer.seek(0)
        return zip_buffer

    async def get_zip_stream(self, media_urls: List[str], username: str):
        zip_buffer = await self.create_bulk_zip(media_urls, username)
        return zip_buffer
