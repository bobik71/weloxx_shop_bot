# test_lzt_search.py
import asyncio
import aiohttp
import config

async def test():
    token = config.LZT_TOKEN
    base = config.MARKET_API_BASE  # https://api.lzt.market
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Тестирование поиска аккаунтов LZT\n")
        
        # === ТЕСТ 1: Проверка токена ===
        print("1️⃣ Проверка токена...")
        async with session.get(f"{base}/me", headers=headers) as resp:
            print(f"   Статус: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                user = data.get('user', {})
                print(f"   ✅ Пользователь: {user.get('username', 'N/A')}")
                print(f"   💰 Баланс: {user.get('convertedBalance', 'N/A')} ₽")
            else:
                text = await resp.text()
                print(f"   ❌ Ошибка: {text[:200]}")
        
        # === ТЕСТ 2: Поиск Telegram аккаунтов без фильтра ===
        print("\n2️⃣ Поиск Telegram аккаунтов (без фильтра)...")
        async with session.get(f"{base}/items", params={"limit": 5}, headers=headers) as resp:
            print(f"   Статус: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                items = data.get('items', [])
                print(f"   ✅ Найдено: {len(items)} аккаунтов")
                for item in items[:3]:
                    title = item.get('title', 'N/A')
                    price = item.get('price', 'N/A')
                    print(f"      • {title} — {price}₽")
            else:
                text = await resp.text()
                print(f"   ❌ Ошибка: {text[:200]}")
        
        # === ТЕСТ 3: Поиск по префиксу США (+1) ===
        print("\n3️⃣ Поиск аккаунтов США (telegram 1)...")
        async with session.get(f"{base}/items", params={"search_query": "telegram 1", "limit": 10}, headers=headers) as resp:
            print(f"   Статус: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                items = data.get('items', [])
                print(f"   ✅ Найдено: {len(items)} аккаунтов")
                for item in items[:5]:
                    title = item.get('title', 'N/A')
                    price = item.get('price', 'N/A')
                    print(f"      • {title} — {price}₽")
            else:
                text = await resp.text()
                print(f"   ❌ Ошибка: {text[:200]}")
        
        # === ТЕСТ 4: Поиск по префиксу Украины (+380) ===
        print("\n4️⃣ Поиск аккаунтов Украина (telegram 380)...")
        async with session.get(f"{base}/items", params={"search_query": "telegram 380", "limit": 10}, headers=headers) as resp:
            print(f"   Статус: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                items = data.get('items', [])
                print(f"   ✅ Найдено: {len(items)} аккаунтов")
                for item in items[:5]:
                    title = item.get('title', 'N/A')
                    price = item.get('price', 'N/A')
                    print(f"      • {title} — {price}₽")
            else:
                text = await resp.text()
                print(f"   ❌ Ошибка: {text[:200]}")

if __name__ == "__main__":
    asyncio.run(test())
