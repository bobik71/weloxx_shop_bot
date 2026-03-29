# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные из .env
load_dotenv()

# 📁 Пути
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = os.getenv("DB_PATH", DATA_DIR / "store.db")

# 🔑 Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')

# 🔑 LZT Market API
LZT_TOKEN = os.getenv('LZT_TOKEN')
MARKET_API_BASE = "https://api.lzt.market"
FORUM_API_BASE = "https://prod-api.lolz.live"
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 10))
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', 2))

# 💰 Платёжные системы
CRYPTOBOT_TOKEN = os.getenv('CRYPTOBOT_TOKEN')
CRYPTOCLOUD_TOKEN = os.getenv('CRYPTOCLOUD_TOKEN')

# 🔐 Безопасность
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'change-me-32-chars-minimum!!')
ADMIN_IDS = os.getenv('ADMIN_IDS', '')

# ✅ Валидация конфигурации
def check_config():
    errors = []
    if not BOT_TOKEN:
        errors.append("❌ BOT_TOKEN не задан")
    if not LZT_TOKEN:
        errors.append("❌ LZT_TOKEN не задан")
    if LZT_TOKEN and len(LZT_TOKEN) < 100:
        errors.append("❌ LZT_TOKEN слишком короткий")
    if ENCRYPTION_KEY == 'change-me-32-chars-minimum!!':
        errors.append("❌ ENCRYPTION_KEY не изменён")
    
    if errors:
        print("⚠️ ОШИБКИ КОНФИГУРАЦИИ:")
        for err in errors:
            print(f"   {err}")
        return False
    
    print("✅ Конфигурация проверена успешно")
    return True

# config.py — добавьте в конец
TELEGRAM_ACCOUNTS = [
    {
        "code": "US",
        "name": "США",
        "flag": "🇺🇸",
        "prefix": "+1",
        "price": 150
    },
    {
        "code": "RU",
        "name": "Россия",
        "flag": "🇷🇺",
        "prefix": "+7",
        "price": 100
    },
    {
        "code": "GB",
        "name": "Великобритания",
        "flag": "🇬🇧",
        "prefix": "+44",
        "price": 200
    }
]

SUPPORT_CHAT = os.getenv('SUPPORT_CHAT', '@support')
BOT_NAME = os.getenv('BOT_NAME', 'Weloxx Shop')