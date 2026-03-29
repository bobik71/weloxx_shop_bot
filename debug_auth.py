# debug_auth.py
import requests
import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Получаем токен
TOKEN = os.getenv('LZT_TOKEN') or os.getenv('LZT_API_KEY')

print("🔍 ДИАГНОСТИКА АВТОРИЗАЦИИ LZT")
print("=" * 50)

# 1. Проверка токена
print(f"\n1️⃣ Токен загружен: {bool(TOKEN)}")
if TOKEN:
    print(f"   Длина: {len(TOKEN)} символов")
    print(f"   Начинается с 'ey': {TOKEN.startswith('ey')}")
    print(f"   Есть пробелы: {' ' in TOKEN}")
    print(f"   Есть переносы: {'\\n' in TOKEN or '\\r' in TOKEN}")
    
    # Очищаем токен от мусора
    TOKEN = TOKEN.strip().replace('\n', '').replace('\r', '')
else:
    print("   ❌ Токен пустой! Проверьте .env")

# 2. Проверка заголовка
if TOKEN:
    auth_header = f"Bearer {TOKEN}"
    print(f"\n2️⃣ Заголовок Authorization:")
    print(f"   Первые 30 симв: {auth_header[:30]}...")
    print(f"   Последние 20 симв: ...{auth_header[-20:]}")

# 3. Тестовые запросы к разным API
print(f"\n3️⃣ Тестовые запросы:")

endpoints = [
    ("Forum API", "https://prod-api.lolz.live/user"),
    ("Market API", "https://api.lzt.market/me"),
    ("Market Status", "https://api.lzt.market/status"),  # Публичный, без авторизации
]

for name, url in endpoints:
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        status = resp.status_code
        # Скрываем чувствительные данные в ответе
        preview = resp.text[:150].replace(TOKEN[:20] if TOKEN else "", "***") if resp.text else "пустой ответ"
        print(f"   {name}: {status} → {preview}")
    except Exception as e:
        print(f"   {name}: ❌ Ошибка соединения: {e}")

print("\n" + "=" * 50)
print("📋 Интерпретация:")
print("   • 200 → ✅ Токен работает!")
print("   • 401 → ❌ Токен недействителен (отозван/неверный)")
print("   • 403 → ⚠️ Токен валиден, но нет прав на эндпоинт")
print("   • 404 → ❓ Неверный URL эндпоинта")
print("   • Ошибка соединения → 🌐 Проблемы с сетью/DNS")