from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🔍 Каталог", callback_data="catalog"),
        InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")
    )
    b.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="help")
    )
    return b.as_markup()

def back_kb(cb: str = "main_menu") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data=cb))
    return b.as_markup()