# test_all_urls.py
import asyncio
import aiohttp

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJzdWIiOjk4NzQ1NzQsImlzcyI6Imx6dCIsImlhdCI6MTc3NDYxODMzNiwianRpIjoiOTUyMjA3Iiwic2NvcGUiOiJiYXNpYyByZWFkIHBvc3QgY29udmVyc2F0ZSBwYXltZW50IGludm9pY2UgY2hhdGJveCBtYXJrZXQiLCJleHAiOjE5MzIyOTgzMzZ9.mACtGrDqS_r-TAF3oIvEzs4fIrhsC0LNHKfJYSNXsHVQUVmwDw5-Mqd6GTfZJWUPNnFh0zxlV3p5cKoGoSggEcDd8PeCwiWoqYkK1DgcGW-1QYxK3jpaRop5pukirk6w1zozB3mJn50Z2Qr61YZXXL_5_2TA4DomUmWZodrXVKE"

BASE_URLS = [
    "https://api.lzt.market",
    "https://api.zelenka.guru",
    "https://lzt.market/api",
    "https://market.lzt.dev",
]

ENDPOINTS = [
    "/v1/user/money",
    "/v1/user",
    "/user/money",
    "/user",
]

async def test_url(session, base, endpoint):
    url = f"{base}{endpoint}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        async with session.get(url, headers=headers, timeout=5) as resp:
            if resp.status != 404:
                print(f"✅ {url} → {resp.status}")
                return True
    except:
        pass
    return False

async def main():
    print("🔍 Поиск рабочего URL...\n")
    async with aiohttp.ClientSession() as session:
        for base in BASE_URLS:
            for endpoint in ENDPOINTS:
                await test_url(session, base, endpoint)

asyncio.run(main())