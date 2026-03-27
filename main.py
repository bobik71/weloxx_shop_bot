# main.py (самые первые строки)
import sys
from pathlib import Path

# Добавляем корень проекта в путь импортов
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Дальше обычные импорты
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
...
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import config
from core.database import init_db
from handlers import start, catalog, cart, admin
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Выполняется при запуске бота"""
    await init_db()
    
    # ✅ Получаем инфо о боте (await обязательно!)
    bot_info = await bot.get_me()
    logger.info(f"✅ Бот запущен: @{bot_info.username}")
    
    # Устанавливаем команды
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🏠 Главное меню"),
        types.BotCommand(command="admin", description="⚙️ Админ-панель"),
    ])

async def main():
    """Точка входа"""
    # Создаём бота с настройками по умолчанию
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаём диспетчер
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем роутеры (обработчики)
    dp.include_routers(start.router, catalog.router, cart.router, admin.router)
    
    # Регистрируем startup-хук
    dp.startup.register(on_startup)
    
    # Запускаем polling
    logger.info("🔄 Запуск polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}", exc_info=True)