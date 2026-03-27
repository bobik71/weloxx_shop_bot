from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def categories_kb(cats: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for c in cats[:10]:
        b.button(text=f"🎮 {c.title()}", callback_data=f"cat_{c}")
    b.adjust(2)
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return b.as_markup()

def account_kb(aid: int, in_cart: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    btn = "✅ В корзине" if in_cart else "🛒 В корзину"
    cb = "in_cart" if in_cart else f"add_{aid}"
    b.row(
        InlineKeyboardButton(text=btn, callback_data=cb),
        InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_{aid}")
    )
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data="catalog"))
    return b.as_markup()