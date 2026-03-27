# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.isdigit()]

# LZT Market API
LZT_TOKEN = os.getenv("LZT_TOKEN", "")
LZT_API_BASE = "https://lzt.market/api/v1"

# Markup
MARKUP_PERCENT = int(os.getenv("MARKUP_PERCENT", "20"))

# Database
DB_PATH = os.getenv("DB_PATH", "data/store.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-me-32-chars-minimum!!")

# Payment
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
CRYPTOBOT_TESTNET = os.getenv("CRYPTOBOT_TESTNET", "true").lower() == "true"

# Bot
BOT_NAME = "Telegram Accounts Shop"
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "@support")

# Limits
API_REQUESTS_PER_MIN = 300
API_TIMEOUT = 60

# 🔹 СПИСОК СТРАН (каталог)
TELEGRAM_ACCOUNTS = [
    {"code": "US", "flag": "🇺🇸", "name": "США", "prefix": "+1", "price": 40},
    {"code": "MM", "flag": "🇲🇲", "name": "Мьянма", "prefix": "+95", "price": 40},
    {"code": "IN", "flag": "🇮🇳", "name": "Индия", "prefix": "+91", "price": 45},
    {"code": "CO", "flag": "🇨🇴", "name": "Колумбия", "prefix": "+57", "price": 45},
    {"code": "KE", "flag": "🇰🇪", "name": "Кения", "prefix": "+254", "price": 45},
    {"code": "CA", "flag": "🇨🇦", "name": "Канада", "prefix": "+1", "price": 50},
    {"code": "ID", "flag": "🇮🇩", "name": "Индонезия", "prefix": "+62", "price": 50},
    {"code": "BD", "flag": "🇧🇩", "name": "Бангладеш", "prefix": "+880", "price": 50},
    {"code": "EG", "flag": "🇪🇬", "name": "Египет", "prefix": "+20", "price": 55},
    {"code": "AR", "flag": "🇦🇷", "name": "Аргентина", "prefix": "+54", "price": 65},
    {"code": "VN", "flag": "🇻🇳", "name": "Вьетнам", "prefix": "+84", "price": 70},
    {"code": "GB", "flag": "🇬🇧", "name": "Великобритания", "prefix": "+44", "price": 80},
    {"code": "AF", "flag": "🇦🇫", "name": "Афганистан", "prefix": "+93", "price": 80},
    {"code": "BR", "flag": "🇧🇷", "name": "Бразилия", "prefix": "+55", "price": 85},
    {"code": "EC", "flag": "🇪🇨", "name": "Эквадор", "prefix": "+593", "price": 85},
    {"code": "PH", "flag": "🇵🇭", "name": "Филиппины", "prefix": "+63", "price": 90},
    {"code": "UZ", "flag": "🇺🇿", "name": "Узбекистан", "prefix": "+998", "price": 90},
    {"code": "TH", "flag": "🇹🇭", "name": "Таиланд", "prefix": "+66", "price": 100},
    {"code": "DZ", "flag": "🇩🇿", "name": "Алжир", "prefix": "+213", "price": 100},
    {"code": "YE", "flag": "🇾🇪", "name": "Йемен", "prefix": "+967", "price": 120},
    {"code": "MX", "flag": "🇲🇽", "name": "Мексика", "prefix": "+52", "price": 120},
    {"code": "ES", "flag": "🇪🇸", "name": "Испания", "prefix": "+34", "price": 130},
    {"code": "VE", "flag": "🇻🇪", "name": "Венесуэла", "prefix": "+58", "price": 140},
    {"code": "MY", "flag": "🇲🇾", "name": "Малайзия", "prefix": "+60", "price": 140},
    {"code": "PE", "flag": "🇵🇪", "name": "Перу", "prefix": "+51", "price": 140},
    {"code": "KZ", "flag": "🇰🇿", "name": "Казахстан", "prefix": "+7", "price": 150},
    {"code": "FR", "flag": "🇫🇷", "name": "Франция", "prefix": "+33", "price": 170},
    {"code": "UA", "flag": "🇺🇦", "name": "Украина", "prefix": "+380", "price": 180},
]