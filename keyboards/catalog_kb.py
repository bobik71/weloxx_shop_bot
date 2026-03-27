# keyboards/catalog_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def categories_kb(cats: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for c in cats:
        icon = "📱" if c == "telegram" else "🎮"
        builder.button(text=f"{icon} {c.title()}", callback_data=f"cat_{c}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()

def account_kb(item_id: int, price: float) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_{item_id}_{price}")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="catalog"))
    return builder.as_markup()