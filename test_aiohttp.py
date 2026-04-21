# test_aiohttp.py
import asyncio
import sys

# 🔧 ProactorEventLoop для Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_aiohttp():
    try:
        from aiohttp import ClientSession, TCPConnector
        from aiohttp.resolver import AsyncResolver
        
        connector = TCPConnector(
            resolver=AsyncResolver(nameservers=["8.8.8.8", "1.1.1.1"])
        )
        
        async with ClientSession(connector=connector) as session:
            async with session.get("https://api.telegram.org", timeout=10) as resp:
                print(f"✅ aiohttp: статус {resp.status}")
                return True
    except Exception as e:
        print(f"❌ aiohttp ошибка: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_aiohttp())
    if result:
        print("🎉 aiohttp работает! Проблема была в event loop.")
    else:
        print("⚠️ aiohttp не работает — проверьте версии пакетов.")