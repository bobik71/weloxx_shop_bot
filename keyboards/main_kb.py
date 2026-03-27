# keyboards/main_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # 🔹 Основная кнопка - Каталог (Telegram аккаунты)
    builder.row(
        InlineKeyboardButton(text="📱 Каталог", callback_data="catalog")
    )
    
    # Дополнительные
    builder.row(
        InlineKeyboardButton(text="👤 Мои покупки", callback_data="orders"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="help")
    )
    
    return builder.as_markup()

def back_kb(cb: str = "main_menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=cb))
    return builder.as_markup()