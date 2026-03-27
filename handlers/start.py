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
        f"📱 <b>Telegram аккаунты разных стран</b>\n\n"
        f"🔹 Мгновенная выдача\n"
        f"🔹 Гарантия 24 часа\n"
        f"🔹 Поддержка 24/7\n\n"
        f"Нажмите «📱 Купить аккаунт»:"
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

@router.callback_query(F.data == "orders")
async def show_orders(callback: types.CallbackQuery):
    await callback.answer("📚 История покупок скоро будет!", show_alert=True)

@router.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    await callback.answer(
        f"📞 Поддержка: {config.SUPPORT_CHAT}\n"
        f"⏱️ Гарантия: 24 часа\n"
        f"💳 Оплата: CryptoBot",
        show_alert=True
    )