# keyboards/catalog_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def account_kb(item_id: int, price: float, page: int = 0, total: int = 1) -> InlineKeyboardMarkup:
    """Кнопки для карточки товара"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка купить
    builder.row(
        InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_{item_id}_{price}")
    )
    
    # Навигация если товаров > 1
    if total > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"prev_{page}"))
        if page < total - 1:
            nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"next_{page}"))
        if nav_buttons:
            builder.row(*nav_buttons)
    
    # Кнопка назад
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu"))
    
    return builder.as_markup()

# 🔹 Для будущего расширения (сейчас не используется)
# def categories_kb(cats: list) -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     for c in cats:
#         icon = "📱" if c == "telegram" else "🎮"
#         builder.button(text=f"{icon} {c.title()}", callback_data=f"cat_{c}")
#     builder.adjust(2)
#     builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
#     return builder.as_markup()s