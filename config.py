import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.isdigit()]

# LZT Market API - ✅ ПРОВЕРЕННЫЕ РАБОЧИЕ URL
LZT_TOKEN = os.getenv("LZT_TOKEN", "")
LZT_API_BASE = "https://lzt.market/api/v1"

# Database
DB_PATH = os.getenv("DB_PATH", "data/store.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-me-32-chars-minimum!!")

# Payment
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
CRYPTOBOT_TESTNET = os.getenv("CRYPTOBOT_TESTNET", "true").lower() == "true"

# Bot
BOT_NAME = os.getenv("BOT_NAME", "LZT Store Bot")
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT")

# Limits
API_REQUESTS_PER_MIN = 300
API_TIMEOUT = 30