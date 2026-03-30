# handlers/start.py
from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from core.database import get_or_create_user, get_db
from keyboards.main_kb import main_menu
import config
import logging

logger = logging.getLogger(__name__)
router = Router()

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на обязательный канал"""
    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Проверяем подписку
    is_subscribed = await check_subscription(message.bot, message.from_user.id)
    
    if not is_subscribed:
        # Отправляем сообщение с требованием подписаться
        join_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{config.REQUIRED_CHANNEL.lstrip('@')}")],
                [types.InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
            ]
        )
        await message.answer(
            f"⚠️ <b>Для использования бота необходимо подписаться на наш канал!</b>\n\n"
            f"👉 Нажмите кнопку ниже, чтобы подписаться на {config.REQUIRED_CHANNEL}, "
            f"затем нажмите «✅ Я подписался»",
            reply_markup=join_keyboard,
            parse_mode="HTML"
        )
        return
    
    # Если подписан - продолжаем как обычно
    session = await get_db()
    try:
        await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
    finally:
        await session.close()
    
    text = (
        f"👋 Привет, {message.from_user.first_name or 'пользователь'}!\n\n"
        f"🛍️ <b>{getattr(config, 'BOT_NAME', 'Weloxx Shop')}</b>\n\n"
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

@router.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: types.CallbackQuery):
    """Обработчик кнопки проверки подписки"""
    is_subscribed = await check_subscription(callback.bot, callback.from_user.id)
    
    if is_subscribed:
        await callback.message.delete()
        session = await get_db()
        try:
            await get_or_create_user(
                session,
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name
            )
        finally:
            await session.close()
        
        text = (
            f"👋 Привет, {callback.from_user.first_name or 'пользователь'}!\n\n"
            f"🛍️ <b>{getattr(config, 'BOT_NAME', 'Weloxx Shop')}</b>\n\n"
            f"📱 <b>Telegram аккаунты разных стран</b>\n\n"
            f"🔹 Мгновенная выдача\n"
            f"🔹 Гарантия 24 часа\n"
            f"🔹 Поддержка 24/7\n\n"
            f"Нажмите «📱 Купить аккаунт»:"
        )
        
        await callback.message.answer(
            text,
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Вы еще не подписались на канал!", show_alert=True)

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
        f"📞 Поддержка: {getattr(config, 'SUPPORT_CHAT', '@support')}\n"
        f"⏱️ Гарантия: 24 часа\n"
        f"💳 Оплата: CryptoBot",
        show_alert=True
    )
