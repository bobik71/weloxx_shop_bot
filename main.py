# main.py — Полностью переписан для стабильной работы на Windows
# ==============================================================================
# ⚠️ ВАЖНО: Эти 4 строки ДОЛЖНЫ быть САМЫМИ ПЕРВЫМИ в файле.
# Они исправляют сетевой стек asyncio/aiohttp на Windows.
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

# Загружаем .env ДО чтения переменных
load_dotenv()

# Настройка логирования
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
    # 1. Читаем токен напрямую (чтобы config.py не крашил бот при отсутствии .env)
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token or len(bot_token) < 30:
        logger.error("❌ BOT_TOKEN не задан или некорректен в .env")
        return

    # 2. Создаём сессию и бота (БЕЗ kwargs — так работает стабильно в aiogram 3.x)
    session = AiohttpSession()
    bot = Bot(token=bot_token, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Безопасное подключение роутеров
    try:
        from handlers import router as main_router
        dp.include_router(main_router)
        logger.info("✅ Роутеры подключены")
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта роутеров: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Роутеры не подключены: {type(e).__name__}")

    # 4. Проверка LZT API (не блокирует запуск)
    lzt_token = os.getenv("LZT_TOKEN", "").strip()
    if lzt_token:
        try:
            from core.lzt_api import LZTClient
            lzt = LZTClient()
            status = lzt.check_connection()
            if status.get("success"):
                logger.info(f"✅ LZT API: {status.get('username')} | Баланс: {status.get('balance')}₽")
            else:
                logger.warning("⚠️ LZT API недоступен. Проверьте токен.")
        except Exception as e:
            logger.warning(f"⚠️ LZT API проверка пропущена: {e}")
    else:
        logger.warning("⚠️ LZT_TOKEN не задан — функции маркета отключены")

    # 5. Инициализация БД
    try:
        from core.database import init_db
        await init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")

    # 6. Тест подключения к Telegram
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот запущен: @{me.username} (ID: {me.id})")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Telegram: {type(e).__name__}: {e}")
        await bot.session.close()
        return

    # 7. Запуск polling
    logger.info("🔄 Запуск long polling...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по Ctrl+C")
    finally:
        await bot.session.close()
        logger.info("🔚 Сессия закрыта. Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Прервано пользователем")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {type(e).__name__}: {e}", exc_info=True)