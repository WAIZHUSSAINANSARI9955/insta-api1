import httpx
import asyncio

async def replicate_500():
    url = "http://localhost:8000/profile/rivamumtaz1"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.get(url)
            print(f"Status: {r.status_code}")
            if r.status_code == 500:
                print(f"Error Detail: {r.text}")
            else:
                print(f"Output: {r.text[:500]}")
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    asyncio.run(replicate_500())
