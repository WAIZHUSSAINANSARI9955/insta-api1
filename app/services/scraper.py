import httpx
import json
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from ..utils.helpers import get_random_headers, random_delay

class InstagramScraper:
    def __init__(self):
        self.base_url = "https://www.instagram.com"

    async def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{username}/"
        headers = get_random_headers()

        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
            await random_delay()
            response = await client.get(url)
            
            if response.status_code != 200:
                print(f"Failed to fetch profile: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, "lxml")
            
            # Instagram often embeds data in JSON in a script tag
            # We look for sharedData or additionalData
            script_tag = soup.find("script", string=re.compile("window._sharedData"))
            
            if script_tag:
                json_text = re.search(r"window._sharedData\s*=\s*({.*?});", script_tag.string).group(1)
                data = json.loads(json_text)
                user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
            else:
                # Alternative: Some modern versions use a different structure or we might need to look at __additionalData
                # Or just manually parse what we can from meta tags if JSON is missing
                user_data = self._parse_from_meta(soup, username)
                if not user_data:
                    return None

            return self._format_user_data(user_data)

    def _parse_from_meta(self, soup: BeautifulSoup, username: str) -> Dict[str, Any]:
        description = soup.find("meta", property="og:description")
        title = soup.find("meta", property="og:title")
        image = soup.find("meta", property="og:image")

        desc_content = description["content"] if description else ""
        # Example desc: "1,234 Followers, 567 Following, 89 Posts - See Instagram photos and videos from Full Name (@username)"
        
        followers = 0
        following = 0
        posts = 0
        
        try:
            match = re.search(r"([\d,]+)\s*Followers,\s*([\d,]+)\s*Following,\s*([\d,]+)\s*Posts", desc_content)
            if match:
                followers = int(match.group(1).replace(",", ""))
                following = int(match.group(2).replace(",", ""))
                posts = int(match.group(3).replace(",", ""))
        except Exception:
            pass

        full_name = username
        if title:
            # Example title: "Full Name (@username) • Instagram photos and videos"
            full_name = title["content"].split("(@")[0].strip()

        return {
            "username": username,
            "full_name": full_name,
            "profile_pic": image["content"] if image else None,
            "followers_count": followers,
            "following_count": following,
            "posts_count": posts,
            "media": [] # Meta tags don't give media list
        }

    def _format_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # This formats the graphql user data if available
        # If media isn't in graphql (often it is), we'd need to parse it
        media_list = []
        nodes = user_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
        
        for edge in nodes:
            node = edge["node"]
            media_type = "post"
            if node.get("is_video"):
                media_type = "video" if not node.get("product_type") == "clips" else "reel"
            
            media_list.append({
                "media_type": media_type,
                "media_url": node.get("display_url") or node.get("video_url"),
                "thumbnail_url": node.get("display_url"),
                "caption": node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", "") if node.get("edge_media_to_caption", {}).get("edges") else "",
                "created_at": node.get("taken_at_timestamp")
            })

        return {
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name"),
            "profile_pic": user_data.get("profile_pic_url_hd") or user_data.get("profile_pic_url"),
            "followers_count": user_data.get("edge_followed_by", {}).get("count", 0),
            "following_count": user_data.get("edge_follow", {}).get("count", 0),
            "posts_count": user_data.get("edge_owner_to_timeline_media", {}).get("count", 0),
            "media": media_list
        }
