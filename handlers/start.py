# handlers/start.py
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from core.database import get_or_create_user
from keyboards.main_kb import main_menu
import config

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"🛍️ <b>{config.BOT_NAME}</b>\n\n"
        "📱 <b>Telegram аккаунты</b>\n"
        "🔹 Мгновенная выдача\n"
        "🔹 Гарантия 24 часа\n"
        "🔹 Поддержка 24/7\n\n"
        "Нажмите «📱 Каталог» для просмотра:"
    )
    
    await message.answer(
        text,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🏠 Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()