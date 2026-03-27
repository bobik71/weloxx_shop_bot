# keyboards/catalog_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def countries_kb(accounts: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком стран"""
    builder = InlineKeyboardBuilder()
    
    # Группируем по 2 в ряд
    for acc in accounts:
        builder.button(
            text=f"{acc['flag']} {acc['name']} — {acc['price']}₽",
            callback_data=f"country_{acc['code']}"
        )
    
    builder.adjust(2)  # 2 кнопки в ряд
    
    # Кнопка назад
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu"))
    
    return builder.as_markup()

def account_kb(item_id: int, price: float, country_code: str) -> InlineKeyboardMarkup:
    """Клавиатура для покупки аккаунта"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка купить
    builder.row(
        InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_{item_id}_{price}_{country_code}")
    )
    
    # Кнопка назад к странам
    builder.row(InlineKeyboardButton(text="🔙 Другая страна", callback_data="back_countries"))
    
    return builder.as_markup()