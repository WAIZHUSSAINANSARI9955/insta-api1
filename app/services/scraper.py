import httpx
import asyncio
import random
import json
import re
import os
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

class InstagramScraper:
    def __init__(self):
        self.base_url = "https://www.instagram.com"
        self.session_id = os.getenv("INSTAGRAM_SESSION_ID")

    def _build_headers(self, mobile: bool = False) -> dict:
        if mobile:
            ua = "Instagram 219.0.0.12.117 Android (30/11; 480dpi; 1080x2186; vivo; V2031; V2031; qcom; en_US; 332152841)"
            app_id = "1217981644879628"
        else:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            app_id = "936619743392459"

        h = {
            "User-Agent": ua,
            "X-IG-App-ID": app_id,
            "X-ASBD-ID": "129477",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
        }
        if self.session_id:
            h["Cookie"] = (
                f"sessionid={self.session_id}; "
                f"ds_user_id={self.session_id.split('%')[0]}; "
                f"csrftoken=DummyToken; mid=Y1; ig_did=D7E8;"
            )
        return h

    async def _fetch_feed_pages(self, client: httpx.AsyncClient, username: str, max_videos: int = 50) -> List[Dict]:
        """Fetch multiple pages of feed using max_id pagination to get more videos."""
        all_items = []
        max_id = None
        page = 0
        max_pages = 5  # Safety cap: 5 pages * ~12 items = ~60 items

        while page < max_pages and len(all_items) < max_videos:
            try:
                url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/"
                params = {"count": 12}
                if max_id:
                    params["max_id"] = max_id

                if page > 0:
                    await asyncio.sleep(random.uniform(2, 4))

                r = await client.get(url, params=params)
                if r.status_code != 200:
                    print(f"DEBUG: Feed page {page+1} failed with {r.status_code}")
                    break

                data = r.json()
                items = data.get("items", [])
                if not items:
                    break

                all_items.extend(items)
                print(f"DEBUG: Feed page {page+1}: fetched {len(items)} items (total: {len(all_items)})")

                # Check if more pages exist
                if not data.get("more_available", False):
                    print(f"DEBUG: No more pages available after page {page+1}.")
                    break

                max_id = data.get("next_max_id")
                if not max_id:
                    break

                page += 1

            except Exception as e:
                print(f"DEBUG: Feed pagination error on page {page+1}: {e}")
                break

        return all_items

    async def _fetch_reels_page(self, client: httpx.AsyncClient, username: str) -> List[Dict]:
        """Fetch reels separately - they often appear here but not in feed."""
        try:
            url = f"https://www.instagram.com/{username}/reels/?__a=1&__d=dis"
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                edges = data.get("graphql", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
                print(f"DEBUG: Reels page found {len(edges)} items.")
                return edges
        except Exception as e:
            print(f"DEBUG: Reels page error: {e}")
        return []

    async def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        username = username.strip().lower().split('?')[0].split('/')[-1].replace("@", "")

        # Use a common client for all requests to maintain cookies if needed
        async with httpx.AsyncClient(headers=self._build_headers(), follow_redirects=True, timeout=30.0) as client:
            
            # ===== STRATEGY 1: web_profile_info (Mobile & Desktop) =====
            # We try with different App IDs as some are less rate-limited
            for use_mobile in [False, True]:
                try:
                    mode = "Mobile" if use_mobile else "Desktop"
                    print(f"DEBUG: Strategy 1 ({mode}) for {username}...")
                    headers = self._build_headers(mobile=use_mobile)
                    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
                    r = await client.get(url, headers=headers)
                    if r.status_code == 200:
                        data = r.json()
                        user = data.get("data", {}).get("user")
                        if user and user.get("username"):
                            print(f"DEBUG: Strategy 1 ({mode}) SUCCESS.")
                            # Fetch more media to reach the target of 30+
                            extra_items = await self._fetch_feed_pages(client, username, max_videos=60)
                            return self._format_user_data(user, extra_items)
                    elif r.status_code == 429:
                        print(f"DEBUG: Strategy 1 ({mode}) Rate Limited.")
                    else:
                        print(f"DEBUG: Strategy 1 ({mode}) returned {r.status_code}")
                except Exception as e:
                    print(f"DEBUG: Strategy 1 ({mode}) error: {e}")
                
                if use_mobile is False: # Small sleep before trying mobile
                    await asyncio.sleep(random.uniform(1, 2))

            # ===== STRATEGY 2: Feed API + Mobile Info Metadata Fallback =====
            print(f"DEBUG: Strategy 2 (Feed + Mobile Info) for {username}...")
            try:
                # 1. Fetch paginated media (Target 60 items)
                feed_items = await self._fetch_feed_pages(client, username, max_videos=60)
                
                profile_user = {}
                pk = None
                
                # Try to get PK from feed items
                if feed_items:
                    item_user = feed_items[0].get("user", {})
                    pk = item_user.get("pk") or item_user.get("id")
                    profile_user["username"] = item_user.get("username", username)
                    profile_user["full_name"] = item_user.get("full_name")
                    profile_user["profile_pic_url"] = item_user.get("hd_profile_pic_url_info", {}).get("url") or item_user.get("profile_pic_url")
                
                # 2. Fetch Mobile Info for full metadata (Followers, Bio, HD Pic)
                if pk:
                    try:
                        print(f"DEBUG: Fetching mobile info for PK {pk}...")
                        mobile_headers = self._build_headers(mobile=True)
                        info_url = f"https://i.instagram.com/api/v1/users/{pk}/info/"
                        info_r = await client.get(info_url, headers=mobile_headers)
                        if info_r.status_code == 200:
                            info_data = info_r.json().get("user", {})
                            # Merge info_data into profile_user
                            for key in ["follower_count", "following_count", "biography", "full_name"]:
                                if info_data.get(key):
                                    profile_user[key] = info_data[key]
                            
                            # Update HD pic
                            hd_pic = info_data.get("hd_profile_pic_url_info", {}).get("url") or info_data.get("profile_pic_url")
                            if hd_pic:
                                profile_user["profile_pic_url"] = hd_pic
                            
                            print(f"DEBUG: Mobile Info SUCCESS — followers={profile_user.get('follower_count')}")
                    except Exception as e:
                        print(f"DEBUG: Mobile info fetch failed: {e}")

                # 3. Fallback to HTML Mining if still missing counts
                if not profile_user.get("follower_count"):
                    try:
                        anon_headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                            "Accept": "text/html,application/xhtml+xml",
                        }
                        html_r = await client.get(f"https://www.instagram.com/{username}/", headers=anon_headers)
                        if html_r.status_code == 200:
                            soup = BeautifulSoup(html_r.text, "lxml")
                            meta_user = self._parse_from_meta(soup, username)
                            # Merge only if non-zero
                            if meta_user.get("follower_count"):
                                profile_user["follower_count"] = meta_user["follower_count"]
                                profile_user["following_count"] = meta_user.get("following_count", 0)
                    except: pass

                # Merge and Format
                if feed_items or profile_user.get("username"):
                    print(f"DEBUG: Strategy 2 FINAL — Items: {len(feed_items)}, Followers: {profile_user.get('follower_count', 0)}")
                    return self._format_user_data(profile_user, feed_items)

            except Exception as e:
                print(f"DEBUG: Strategy 2 error: {e}")

        return None

    def _deep_find(self, obj: Any, username: str) -> Optional[Dict[str, Any]]:
        if isinstance(obj, dict):
            if obj.get("username") == username: return obj
            for k in ["user", "graphql", "data", "entry_data"]:
                if k in obj:
                    res = self._deep_find(obj[k], username)
                    if res: return res
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    res = self._deep_find(v, username)
                    if res: return res
        elif isinstance(obj, list):
            for item in obj:
                res = self._deep_find(item, username)
                if res: return res
        return None

    def _format_user_data(self, user: Dict[str, Any], items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        media_list = []

        # Combine all possible media sources
        timeline = user.get("edge_owner_to_timeline_media") or user.get("edge_v_contents") or {}
        edges = timeline.get("edges", []) or []
        # Merge graphql edges + feed API items (deduplicate by url)
        seen_urls = set()
        all_raw = list(edges) + (items if items else []) + list(user.get("items", []))

        for edge in all_raw:
            try:
                main_node = edge.get("node", edge)
                if not main_node: continue

                # Handle carousel posts
                sidecar = main_node.get("edge_sidecar_to_children", {}).get("edges", [])
                nodes_to_process = [main_node] if not sidecar else [e.get("node", e) for e in sidecar]

                for node in nodes_to_process:
                    v_url = (
                        node.get("video_url") or
                        (node.get("video_versions", [{}])[0].get("url") if node.get("video_versions") else None) or
                        node.get("display_url")
                    )
                    t_url = (
                        node.get("display_url") or
                        node.get("thumbnail_src") or
                        (node.get("image_versions2", {}).get("candidates", [{}])[0].get("url") if node.get("image_versions2") else None)
                    )
                    if not v_url or v_url in seen_urls: continue
                    seen_urls.add(v_url)

                    media_list.append({
                        "media_type": "reel" if node.get("product_type") == "clips" else ("video" if node.get("is_video") else "post"),
                        "media_url": v_url,
                        "thumbnail_url": t_url,
                        "caption": self._get_caption(main_node),
                        "created_at": main_node.get("taken_at_timestamp") or main_node.get("taken_at")
                    })
            except: continue

        # Extract counts from all possible key formats
        f_count = (
            user.get("edge_followed_by", {}).get("count") or
            user.get("follower_count") or
            user.get("followed_by_count") or 0
        )
        ing_count = (
            user.get("edge_follow", {}).get("count") or
            user.get("following_count") or
            user.get("follow_count") or 0
        )
        m_count = (
            user.get("edge_owner_to_timeline_media", {}).get("count") or
            user.get("media_count") or
            len(media_list)
        )

        return {
            "username": user.get("username"),
            "full_name": user.get("full_name") or user.get("username"),
            "biography": user.get("biography") or "",
            "profile_pic_url": (
                user.get("profile_pic_url_hd") or
                user.get("profile_pic_url") or
                user.get("hd_profile_pic_url_info", {}).get("url")
            ),
            "follower_count": f_count,
            "following_count": ing_count,
            "media_count": m_count,
            "media": media_list
        }

    def _get_caption(self, node: Dict[str, Any]) -> str:
        try:
            if "edge_media_to_caption" in node:
                edges = node["edge_media_to_caption"].get("edges", [])
                if edges: return edges[0].get("node", {}).get("text", "")
            cap = node.get("caption")
            if isinstance(cap, dict): return cap.get("text", "")
            if cap: return str(cap)
            return ""
        except: return ""

    def _parse_from_meta(self, soup: BeautifulSoup, username: str) -> Dict[str, Any]:
        """Extract follower/following/post counts from og:description meta tag."""
        desc = soup.find("meta", property="og:description")
        img = soup.find("meta", property="og:image")
        f, ing, p = 0, 0, 0
        if desc:
            content = desc.get("content", "")
            try:
                def p_n(s):
                    s = s.upper().replace(",", "").replace(" ", "")
                    m = 1
                    if "K" in s: m = 1000; s = s.replace("K", "")
                    if "M" in s: m = 1000000; s = s.replace("M", "")
                    return int(float(s) * m)
                f_m = re.search(r"([\d,.]+[KkMm]?)\s*Followers", content, re.I)
                ing_m = re.search(r"([\d,.]+[KkMm]?)\s*Following", content, re.I)
                p_m = re.search(r"([\d,.]+[KkMm]?)\s*Posts", content, re.I)
                if f_m: f = p_n(f_m.group(1))
                if ing_m: ing = p_n(ing_m.group(1))
                if p_m: p = p_n(p_m.group(1))
            except: pass
        return {
            "username": username,
            "full_name": username,
            "biography": "",
            "profile_pic_url": img.get("content") if img else None,
            "follower_count": f,
            "following_count": ing,
            "media_count": p,
            "media": []
        }
