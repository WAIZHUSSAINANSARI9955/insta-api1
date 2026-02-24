import httpx
import asyncio

async def test_backend():
    url = "http://localhost:8000/"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            print(f"Root Status: {r.status_code}")
            print(f"Root Output: {r.json()}")
            
            # Test a profile
            r = await client.get("http://localhost:8000/profile/rjamumtaz1")
            print(f"Profile Status: {r.status_code}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend())
