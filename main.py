# main.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import config
from core.database import init_db
from handlers import start, catalog, cart
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    await init_db()
    bot_info = await bot.get_me()
    logger.info(f"✅ Бот запущен: @{bot_info.username}")
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🏠 Главное меню"),
    ])

async def main():
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