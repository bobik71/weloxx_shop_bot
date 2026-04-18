import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout, TCPConnector, ClientSession
from config import BOT_TOKEN
from core.lzt_api import LZTClient
from core.database import init_db
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

async def main():
    # Настройка сессии с увеличенными таймаутами и принудительным использованием IPv4
    # family=2 (AF_INET) — только IPv4, чтобы избежать проблем с DNS при IPv6
    connector = TCPConnector(family=2, limit=100, keepalive_timeout=30)
    timeout = ClientTimeout(total=30, connect=10, sock_read=10)
    
    # Создаём собственный ClientSession с нужными параметрами
    aiohttp_session = ClientSession(
        connector=connector,
        timeout=timeout
    )
    
    # Передаём готовую сессию в AiohttpSession
    session = AiohttpSession(session=aiohttp_session)
    
    bot = Bot(token=BOT_TOKEN, session=session)
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
    
    # Проверка подключения к Telegram с обработкой ошибок
    try:
        me = await bot.get_me()
        logging.info(f"✅ Бот запущен: @{me.username}")
    except Exception as e:
        logging.error(f"❌ Ошибка подключения к Telegram: {type(e).__name__}: {e}")
        logging.error("Проверьте ваше интернет-соединение и настройки DNS")
        await session.close()
        return

    try:
        await dp.start_polling(bot)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())