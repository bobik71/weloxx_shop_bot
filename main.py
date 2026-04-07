import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from core.lzt_api import LZTClient  # ✅ Исправлено на LZTClient
from core.database import init_db
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # ✅ Проверка подключения при старте
    lzt = LZTClient()
    status = lzt.check_connection()
    if status["success"]:
        logging.info(f"✅ LZT API: {status['username']} | Баланс: {status['balance']}₽")
    else:
        logging.warning("⚠️ Не удалось подключиться к LZT API. Проверьте токен.")

    await init_db()
    logging.info("✅ База данных инициализирована")
    logging.info(f"✅ Бот запущен: @{(await bot.get_me()).username}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())