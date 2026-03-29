# main.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from core.database import init_db
from core.lzt_api import LZTClient
from handlers import start, catalog, cart
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def check_lzt_api():
    """Проверяет подключение к LZT API"""
    try:
        client = LZTClient()
        username = client.get_username()
        balance = client.get_balance()
        logger.info(f"✅ LZT API: {username} | Баланс: {balance}₽")
        return True
    except Exception as e:
        logger.error(f"❌ LZT API не доступен: {e}")
        return False

async def on_startup(bot: Bot):
    # 1. Проверяем API
    if config.LZT_TOKEN and not await check_lzt_api():
        logger.warning("⚠️ Бот запущен, но LZT API не доступен.")
    
    # 2. Инициализация БД
    await init_db()
    
    # 3. Информация о боте
    bot_info = await bot.get_me()
    logger.info(f"✅ Бот запущен: @{bot_info.username}")
    
    # 4. Команды
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🏠 Главное меню"),
    ])

async def main():
    # Проверка конфигурации
    if not config.check_config():
        logger.error("⛔ Конфигурация неверна. Бот не запущен.")
        return
    
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_routers(start.router, catalog.router, cart.router)
    dp.startup.register(on_startup)
    
    logger.info("🔄 Запуск polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}", exc_info=True)