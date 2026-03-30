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
    {"code": "US", "name": "США", "flag": "🇺🇸", "prefix": "+1", "price": 40},
    {"code": "MM", "name": "Мьянма", "flag": "🇲🇲", "prefix": "+95", "price": 40},
    {"code": "IN", "name": "Индия", "flag": "🇮🇳", "prefix": "+91", "price": 45},
    {"code": "CO", "name": "Колумбия", "flag": "🇨🇴", "prefix": "+57", "price": 45},
    {"code": "KE", "name": "Кения", "flag": "🇰🇪", "prefix": "+254", "price": 45},
    {"code": "CA", "name": "Канада", "flag": "🇨🇦", "prefix": "+1", "price": 50},
    {"code": "ID", "name": "Индонезия", "flag": "🇮🇩", "prefix": "+62", "price": 50},
    {"code": "BD", "name": "Бангладеш", "flag": "🇧🇩", "prefix": "+880", "price": 50},
    {"code": "EG", "name": "Египет", "flag": "🇪🇬", "prefix": "+20", "price": 55},
    {"code": "AR", "name": "Аргентина", "flag": "🇦🇷", "prefix": "+54", "price": 65},
    {"code": "VN", "name": "Вьетнам", "flag": "🇻🇳", "prefix": "+84", "price": 70},
    {"code": "GB", "name": "Великобритания", "flag": "🇬🇧", "prefix": "+44", "price": 80},
    {"code": "AF", "name": "Афганистан", "flag": "🇦🇫", "prefix": "+93", "price": 80},
    {"code": "BR", "name": "Бразилия", "flag": "🇧🇷", "prefix": "+55", "price": 85},
    {"code": "EC", "name": "Эквадор", "flag": "🇪🇨", "prefix": "+593", "price": 85},
    {"code": "PH", "name": "Филиппины", "flag": "🇵🇭", "prefix": "+63", "price": 90},
    {"code": "UZ", "name": "Узбекистан", "flag": "🇺🇿", "prefix": "+998", "price": 90},
    {"code": "TH", "name": "Таиланд", "flag": "🇹🇭", "prefix": "+66", "price": 100},
    {"code": "DZ", "name": "Алжир", "flag": "🇩🇿", "prefix": "+213", "price": 100},
    {"code": "YE", "name": "Йемен", "flag": "🇾🇪", "prefix": "+967", "price": 120},
    {"code": "MX", "name": "Мексика", "flag": "🇲🇽", "prefix": "+52", "price": 120},
    {"code": "ES", "name": "Испания", "flag": "🇪🇸", "prefix": "+34", "price": 130},
    {"code": "VE", "name": "Венесуэла", "flag": "🇻🇪", "prefix": "+58", "price": 140},
    {"code": "MY", "name": "Малайзия", "flag": "🇲🇾", "prefix": "+60", "price": 140},
    {"code": "PE", "name": "Перу", "flag": "🇵🇪", "prefix": "+51", "price": 140},
    {"code": "KZ", "name": "Казахстан", "flag": "🇰🇿", "prefix": "+7", "price": 150},
    {"code": "FR", "name": "Франция", "flag": "🇫🇷", "prefix": "+33", "price": 170},
    {"code": "UA", "name": "Украина", "flag": "🇺🇦", "prefix": "+380", "price": 180},
]

SUPPORT_CHAT = os.getenv('SUPPORT_CHAT', '@support')
BOT_NAME = os.getenv('BOT_NAME', 'Weloxx Shop')

# 📢 Канал для обязательной подписки
REQUIRED_CHANNEL = os.getenv('REQUIRED_CHANNEL', '@weloxxsale')
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1001234567890')  # Замените на реальный ID канала