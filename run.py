# start.py — ГАРАНТИРОВАННЫЙ ЗАПУСК НА WINDOWS
# ==============================================================================
import sys, asyncio, os

# ⚠️ САМОЕ ПЕРВОЕ — фикс event loop ДО любых импортов библиотек!
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Теперь импорты
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message

# Минимальная конфигурация (вместо config.py для теста)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    print("❌ Укажите BOT_TOKEN в среде или в .env файле")
    sys.exit(1)

# Простейший хендлер
dp = Dispatcher()
@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer("✅ Бот работает! 🎉")

# Запуск
async def main():
    bot = Bot(token=BOT_TOKEN, session=AiohttpSession())  # ← Без аргументов!
    print(f"🔄 Запуск бота...")
    try:
        me = await bot.get_me()
        print(f"✅ Подключено: @{me.username}")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())