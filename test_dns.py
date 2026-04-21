# test_dns.py
import socket
import ssl
import urllib.request

print("🔍 Тест сети для Telegram Bot API...\n")

# 1. Прямое обращение по IP (если знаете актуальный)
try:
    # Telegram API IP могут меняться, это пример
    ip = socket.gethostbyname("api.telegram.org")
    print(f"✅ DNS-резолвинг: api.telegram.org → {ip}")
except socket.gaierror as e:
    print(f"❌ DNS-резолвинг НЕ работает: {e}")

# 2. HTTPS-запрос через urllib (без aiogram)
try:
    context = ssl.create_default_context()
    with urllib.request.urlopen("https://api.telegram.org", timeout=10, context=context) as resp:
        print(f"✅ HTTPS-запрос успешен: статус {resp.status}")
except Exception as e:
    print(f"❌ HTTPS-запрос НЕ работает: {type(e).__name__}: {e}")

# 3. Проверка прокси-переменной
import os
proxy = os.getenv("TELEGRAM_PROXY")
if proxy:
    print(f"ℹ️ Найден прокси в env: {proxy[:30]}...")
else:
    print("ℹ️ Прокси не задан (переменная TELEGRAM_PROXY пустая)")