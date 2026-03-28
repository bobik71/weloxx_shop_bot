# test_search.py
import asyncio
import aiohttp
import config

async def test():
    token = config.LZT_TOKEN
    base = config.LZT_API_BASE  # https://lzt.market/api/v1
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Тестирование API lzt.market\n")
        
        # === ТЕСТ 1: Проверка токена ===
        print("1️⃣ Проверка токена...")
        async with session.get(f"{base}/user", headers=headers) as resp:
            content_type = resp.headers.get("Content-Type", "")
            print(f"   📡 Статус: {resp.status}")
            print(f"   📄 Content-Type: {content_type}")
            
            if "application/json" in content_type:
                data = await resp.json()
                print(f"   ✅ JSON: {data.get('username', 'OK')}")
            else:
                text = await resp.text()
                print(f"   ❌ HTML: {text[:200]}...")
        
        # === ТЕСТ 2: Разные варианты категорий ===
        print("\n2️⃣ Поиск категорий (разные URL)...")
        
        endpoints_to_try = [
            "/market/categories",
            "/categories", 
            "/market",
            "/items/categories",
        ]
        
        for endpoint in endpoints_to_try:
            print(f"\n   🔹 Пробуем: {endpoint}")
            try:
                async with session.get(f"{base}{endpoint}", headers=headers) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    print(f"      Статус: {resp.status}, Type: {content_type}")
                    
                    if resp.status == 200 and "application/json" in content_type:
                        data = await resp.json()
                        print(f"      ✅ JSON: {str(data)[:150]}...")
                        break
                    else:
                        text = await resp.text()
                        # Показываем первые 100 символов HTML для диагностики
                        clean_text = text.replace("\n", " ").strip()[:100]
                        print(f"      ❌ HTML: {clean_text}...")
            except Exception as e:
                print(f"      💥 Ошибка: {e}")
        
        # === ТЕСТ 3: Поиск Telegram аккаунтов ===
        print("\n3️⃣ Поиск Telegram аккаунтов...")
        
        # Пробуем разные варианты
        search_urls = [
            f"{base}/market/telegram?limit=3",
            f"{base}/telegram?limit=3",
            f"{base}/items/telegram?limit=3",
        ]
        
        for url in search_urls:
            print(f"\n   🔹 {url}")
            try:
                async with session.get(url, headers=headers) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    print(f"      Статус: {resp.status}, Type: {content_type}")
                    
                    if resp.status == 200 and "application/json" in content_type:
                        data = await resp.json()
                        items = data.get("items", data if isinstance(data, list) else [])
                        print(f"      ✅ Найдено: {len(items)} аккаунтов")
                        for item in items[:2]:
                            title = item.get("title", item.get("name", "N/A")) if isinstance(item, dict) else str(item)
                            price = item.get("price", "N/A") if isinstance(item, dict) else "N/A"
                            print(f"         • {title} — {price}₽")
                        break
                    else:
                        text = await resp.text()
                        clean_text = text.replace("\n", " ").strip()[:100]
                        print(f"      ❌ HTML: {clean_text}...")
            except Exception as e:
                print(f"      💥 Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test())