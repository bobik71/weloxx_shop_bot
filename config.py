# config.py — Центральная конфигурация бота Weloxx Shop
import os
from dotenv import load_dotenv

# Загружаем .env из корня проекта
load_dotenv()

# ==================== TELEGRAM ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан в .env")

# Админы: список ID через запятую (например: "123456789,987654321")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = set(int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()) if ADMIN_IDS_RAW else set()

# ==================== ОБЯЗАТЕЛЬНАЯ ПОДПИСКА ====================
# CHANNEL_ID — для API-запросов (get_chat_member). Может быть @username или числовой ID
CHANNEL_ID = os.getenv("CHANNEL_ID", "@weloxxsale")

# REQUIRED_CHANNEL — для отображения в интерфейсе (всегда с @)
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "@weloxxsale")

# ==================== LZT MARKET API ====================
LZT_TOKEN = os.getenv("LZT_TOKEN")
if not LZT_TOKEN:
    raise ValueError("❌ LZT_TOKEN не задан в .env")

LZT_BASE_URL = "https://prod-api.lzt.market"  # ✅ Рабочий эндпоинт
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.5"))

# ==================== CRYPTOBOT (опционально) ====================
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")

# ==================== БАЗА ДАННЫХ ====================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/shop.db")

# ==================== ЛОГИРОВАНИЕ ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log")

# ==================== НАСТРОЙКИ БОТА ====================
BOT_NAME = os.getenv("BOT_NAME", "Weloxx Shop")
CURRENCY = os.getenv("CURRENCY", "RUB")
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/weloxx_support")

# ==================== ПРОВЕРКА КОНФИГУРАЦИИ ====================
def validate_config():
    """Проверяет наличие обязательных переменных"""
    required = ["BOT_TOKEN", "LZT_TOKEN"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise ValueError(f"❌ Отсутствуют обязательные переменные в .env: {', '.join(missing)}")
    
    # Предупреждение, если нет админов
    if not ADMIN_IDS:
        print("⚠️ ADMIN_IDS не задан — админ-команды будут недоступны")
    
    return True

# Запускаем проверку при импорте
validate_config()