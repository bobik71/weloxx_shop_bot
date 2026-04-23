# config.py — Центральная конфигурация бота Weloxx Shop
import os
import logging
from dotenv import load_dotenv

# Загружаем .env из корня проекта
load_dotenv()

logger = logging.getLogger(__name__)

# ==================== TELEGRAM ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
# Не вызываем ошибку сразу - пусть бот сам проверит токен при запуске
if not BOT_TOKEN:
    logger.warning("⚠️ BOT_TOKEN не задан в .env")

# Админы: список ID через запятую (например: "123456789,987654321")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS = {
    int(x.strip()) for x in ADMIN_IDS_RAW.split(",") 
    if x.strip().isdigit()
} if ADMIN_IDS_RAW else set()

if not ADMIN_IDS:
    logger.warning("⚠️ ADMIN_IDS не задан — админ-команды будут недоступны")

# ==================== ОБЯЗАТЕЛЬНАЯ ПОДПИСКА ====================
CHANNEL_ID = os.getenv("CHANNEL_ID", "@weloxxsale").strip()
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", CHANNEL_ID).strip()

# ==================== LZT MARKET API ====================
LZT_TOKEN = os.getenv("LZT_TOKEN", "").strip()
if not LZT_TOKEN:
    logger.warning("⚠️ LZT_TOKEN не задан в .env")

LZT_BASE_URL = "https://prod-api.lzt.market"
try:
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))
except ValueError:
    API_TIMEOUT = 15
    logger.warning("⚠️ API_TIMEOUT некорректен, используется 15")

try:
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.5"))
except ValueError:
    REQUEST_DELAY = 1.5

# ==================== CRYPTOBOT (опционально) ====================
CRYPTOBOT_TOKEN_RAW = os.getenv("CRYPTOBOT_TOKEN", "")
# Очищаем токен от всех возможных скрытых символов
CRYPTOBOT_TOKEN = "".join(CRYPTOBOT_TOKEN_RAW.split()) if CRYPTOBOT_TOKEN_RAW else ""

# Флаг тестовой сети (по умолчанию False - используем продакшен)
CRYPTOBOT_TESTNET = os.getenv("CRYPTOBOT_TESTNET", "false").strip().lower() in ("true", "1", "yes")

if CRYPTOBOT_TOKEN:
    logger.info(f"✅ CRYPTOBOT_TOKEN установлен (длина: {len(CRYPTOBOT_TOKEN)} симв.)")
    # Проверяем, не содержит ли токен подозрительные символы
    if len(CRYPTOBOT_TOKEN) < 10:
        logger.warning("⚠️ CRYPTOBOT_TOKEN слишком короткий!")
else:
    logger.warning("⚠️ CRYPTOBOT_TOKEN не задан в .env")

# ==================== БАЗА ДАННЫХ ====================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/shop.db").strip()

# ==================== ЛОГИРОВАНИЕ ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log").strip()

# ==================== НАСТРОЙКИ БОТА ====================
BOT_NAME = os.getenv("BOT_NAME", "Weloxx Shop").strip()
CURRENCY = os.getenv("CURRENCY", "RUB").strip().upper()
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/weloxx_support").strip()

# ==================== СПИСОК СТРАН ====================
TELEGRAM_ACCOUNTS = [
    {"code": "US", "name": "США", "flag": "🇺🇸", "price": 40, "prefix": "+1"},
    {"code": "MM", "name": "Мьянма", "flag": "🇲🇲", "price": 40, "prefix": "+95"},
    {"code": "IN", "name": "Индия", "flag": "🇮🇳", "price": 45, "prefix": "+91"},
    {"code": "CO", "name": "Колумбия", "flag": "🇨🇴", "price": 45, "prefix": "+57"},
    {"code": "KE", "name": "Кения", "flag": "🇰🇪", "price": 45, "prefix": "+254"},
    {"code": "CA", "name": "Канада", "flag": "🇨🇦", "price": 50, "prefix": "+1"},
    {"code": "ID", "name": "Индонезия", "flag": "🇮🇩", "price": 50, "prefix": "+62"},
    {"code": "BD", "name": "Бангладеш", "flag": "🇧🇩", "price": 50, "prefix": "+880"},
    {"code": "EG", "name": "Египет", "flag": "🇪🇬", "price": 55, "prefix": "+20"},
    {"code": "AR", "name": "Аргентина", "flag": "🇦🇷", "price": 65, "prefix": "+54"},
    {"code": "VN", "name": "Вьетнам", "flag": "🇻🇳", "price": 70, "prefix": "+84"},
    {"code": "GB", "name": "Великобритания", "flag": "🇬🇧", "price": 80, "prefix": "+44"},
    {"code": "AF", "name": "Афганистан", "flag": "🇦🇫", "price": 80, "prefix": "+93"},
    {"code": "BR", "name": "Бразилия", "flag": "🇧🇷", "price": 85, "prefix": "+55"},
    {"code": "EC", "name": "Эквадор", "flag": "🇪🇨", "price": 85, "prefix": "+593"},
    {"code": "PH", "name": "Филиппины", "flag": "🇵🇭", "price": 90, "prefix": "+63"},
    {"code": "UZ", "name": "Узбекистан", "flag": "🇺🇿", "price": 90, "prefix": "+998"},
    {"code": "TH", "name": "Таиланд", "flag": "🇹🇭", "price": 100, "prefix": "+66"},
    {"code": "DZ", "name": "Алжир", "flag": "🇩🇿", "price": 100, "prefix": "+213"},
    {"code": "YE", "name": "Йемен", "flag": "🇾🇪", "price": 120, "prefix": "+967"},
    {"code": "MX", "name": "Мексика", "flag": "🇲🇽", "price": 120, "prefix": "+52"},
    {"code": "ES", "name": "Испания", "flag": "🇪🇸", "price": 130, "prefix": "+34"},
    {"code": "VE", "name": "Венесуэла", "flag": "🇻🇪", "price": 140, "prefix": "+58"},
    {"code": "MY", "name": "Малайзия", "flag": "🇲🇾", "price": 140, "prefix": "+60"},
    {"code": "PE", "name": "Перу", "flag": "🇵🇪", "price": 140, "prefix": "+51"},
    {"code": "KZ", "name": "Казахстан", "flag": "🇰🇿", "price": 150, "prefix": "+7"},
    {"code": "FR", "name": "Франция", "flag": "🇫🇷", "price": 170, "prefix": "+33"},
    {"code": "UA", "name": "Украина", "flag": "🇺🇦", "price": 180, "prefix": "+380"},
]