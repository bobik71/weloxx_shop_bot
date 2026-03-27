# test_search.py
import asyncio, aiohttp, config

async def test():
    token = config.LZT_TOKEN
    base = config.LZT_API_BASE
    
    # Проверяем доступные категории
    async with aiohttp.ClientSession() as session:
        # 1. Проверка категорий
        async with session.get(
            f"{base}/market/categories",
            headers={"Authorization": f"Bearer {token}"}
        ) as resp:
            data = await resp.json()
            print("📂 Категории:")
            for cat in data.get("categories", [])[:10]:
                print(f"   - {cat['name']}")
        
        # 2. Поиск Telegram аккаунтов
        async with session.get(
            f"{base}/market/telegram",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 5}
        ) as resp:
            data = await resp.json()
            print(f"\n🔍 Telegram аккаунты: {resp.status}")
            if resp.status == 200:
                items = data.get("items", [])
                print(f"   Найдено: {len(items)}")
                for item in items[:3]:
                    print(f"   • {item.get('title', 'N/A')} — {item.get('price', 0)}₽")
            else:
                print(f"   Ошибка: {data}")

asyncio.run(test())