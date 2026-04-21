# main.py — САМЫЙ-САМЫЙ ВЕРХ ФАЙЛА
import sys, asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# Конец фикса. Дальше — ваши импорты.

import logging
import os
# ... и так далее

# ==================== НАЧАЛО ФАЙЛА — КРИТИЧЕСКИЙ ФИКС ДЛЯ WINDOWS ====================
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ==============================================================================

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

from config import BOT_TOKEN, ADMIN_IDS, LZT_TOKEN
from core.lzt_api import LZTClient
from core.database import init_db
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/bot.log", encoding="utf-8", mode="a")
    ]
)
logger = logging.getLogger(__name__)
Path("logs").mkdir(exist_ok=True)


async def main():
    # Проверка токена
    if not BOT_TOKEN or len(BOT_TOKEN) < 30:
        logger.error("❌ BOT_TOKEN не задан или некорректен в .env")
        return

    # Простая сессия — aiohttp сам настроит соединение
    session = AiohttpSession()
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключение роутеров
    dp.include_router(router)
    logger.info("✅ Роутеры подключены")

    # Проверка LZT API (не блокирует запуск)
    if LZT_TOKEN:
        try:
            lzt = LZTClient()
            status = lzt.check_connection()
            if status["success"]:
                logger.info(f"✅ LZT API: {status['username']} | Баланс: {status['balance']}₽")
            else:
                logger.warning("⚠️ LZT API: не удалось подключиться. Проверьте токен.")
        except Exception as e:
            logger.warning(f"⚠️ LZT API ошибка: {e}")

    # Инициализация БД
    await init_db()
    logger.info("✅ База данных инициализирована")

    # Тест подключения к Telegram
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот запущен: @{me.username} (ID: {me.id})")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Telegram: {type(e).__name__}: {e}")
        await bot.session.close()
        return

    # Запуск polling
    logger.info("🔄 Запуск polling...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по Ctrl+C")
    finally:
        await bot.session.close()
        logger.info("🔚 Сессии закрыты")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Прервано пользователем")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {type(e).__name__}: {e}", exc_info=True)