# test_lzt_api.py - Тестирование LZT API
import sys
sys.path.insert(0, '/workspace')

from core.lzt_api import LZTClient
import config

print("🔍 Тестирование LZT Market API")
print("=" * 50)

# Проверка токена
if not config.LZT_TOKEN:
    print("❌ LZT_TOKEN не задан в .env файле!")
    sys.exit(1)

print(f"✅ LZT_TOKEN найден (длина: {len(config.LZT_TOKEN)})")
print(f"📡 API Base: {config.LZT_BASE_URL}")
print()

# Создаём клиент
lzt = LZTClient()

# Тест 1: Получение информации о пользователе
print("1️⃣ Тест: Проверка подключения (/me)")
try:
    status = lzt.check_connection()
    if status.get("success"):
        print(f"   ✅ Успешно!")
        print(f"   👤 Username: {status.get('username', 'N/A')}")
        print(f"   💰 Баланс: {status.get('balance', '0')} ₽")
    else:
        print(f"   ❌ Ошибка: {status}")
except Exception as e:
    print(f"   ❌ Исключение: {e}")

print()

# Тест 2: Поиск аккаунтов Telegram без фильтра
print("2️⃣ Тест: Поиск аккаунтов Telegram (/market/telegram)")
try:
    items = lzt.get_items(limit=5)
    if isinstance(items, dict):
        if 'errors' in items and items['errors']:
            print(f"   ❌ Ошибка API: {items['errors']}")
        elif 'items' in items:
            found = len(items['items'])
            print(f"   ✅ Найдено аккаунтов: {found}")
            for i, item in enumerate(items['items'][:3], 1):
                title = item.get('title', 'N/A')[:50]
                price = item.get('price', 0)
                phone = item.get('phone_number', item.get('phone', 'N/A'))
                print(f"   {i}. {title}... | {price}₽ | {phone}")
        elif 'item' in items:
            print(f"   ⚠️ Возвращён один товар вместо списка")
        else:
            print(f"   ⚠️ Неожиданный формат ответа: {list(items.keys())}")
    elif isinstance(items, list):
        print(f"   ✅ Найдено аккаунтов: {len(items)}")
    else:
        print(f"   ❌ Неожиданный тип ответа: {type(items)}")
except Exception as e:
    print(f"   ❌ Исключение: {e}")

print()

# Тест 3: Поиск аккаунтов с фильтром по стране (США +1)
print("3️⃣ Тест: Поиск аккаунтов США (+1)")
try:
    items = lzt.get_items(search_query="1", limit=5)
    if isinstance(items, dict) and 'items' in items:
        found = len(items['items'])
        print(f"   ✅ Найдено аккаунтов: {found}")
        for i, item in enumerate(items['items'][:3], 1):
            title = item.get('title', 'N/A')[:50]
            price = item.get('price', 0)
            phone = item.get('phone_number', item.get('phone', 'N/A'))
            print(f"   {i}. {title}... | {price}₽ | {phone}")
    elif isinstance(items, dict) and 'errors' in items:
        print(f"   ❌ Ошибка API: {items['errors']}")
    else:
        print(f"   ⚠️ Результат: {type(items)}")
except Exception as e:
    print(f"   ❌ Исключение: {e}")

print()

# Тест 4: Поиск аккаунтов с фильтром по стране (Индия +91)
print("4️⃣ Тест: Поиск аккаунтов Индия (+91)")
try:
    items = lzt.get_items(search_query="91", limit=5)
    if isinstance(items, dict) and 'items' in items:
        found = len(items['items'])
        print(f"   ✅ Найдено аккаунтов: {found}")
        for i, item in enumerate(items['items'][:3], 1):
            title = item.get('title', 'N/A')[:50]
            price = item.get('price', 0)
            phone = item.get('phone_number', item.get('phone', 'N/A'))
            print(f"   {i}. {title}... | {price}₽ | {phone}")
    elif isinstance(items, dict) and 'errors' in items:
        print(f"   ❌ Ошибка API: {items['errors']}")
    else:
        print(f"   ⚠️ Результат: {type(items)}")
except Exception as e:
    print(f"   ❌ Исключение: {e}")

print()
print("=" * 50)
print("✅ Тестирование завершено")
