# handlers/catalog.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from core.lzt_client import LZTMarketClient
from keyboards.catalog_kb import account_kb
import config

router = Router()
lzt = LZTMarketClient(config.LZT_TOKEN)

# 🔹 Только Telegram (остальное закомментировано для расширения)
# AVAILABLE_CATEGORIES = ["telegram", "steam", "vk", "epic"]
DEFAULT_CATEGORY = "telegram"

@router.callback_query(F.data == "catalog")
async def show_items(callback: types.CallbackQuery, state: FSMContext):
    """Сразу показываем Telegram аккаунты (без выбора категории)"""
    
    accounts = await lzt.search_accounts(
        category=DEFAULT_CATEGORY,
        price_min=50,
        price_max=500,
        limit=10
    )
    
    if not accounts:
        await callback.answer("⚠️ Нет аккаунтов в продаже", show_alert=True)
        return
    
    # Сохраняем товары в состояние
    await state.update_data(
        category=DEFAULT_CATEGORY,
        items={str(a["item_id"]): a for a in accounts}
    )
    
    await show_item_card(callback, accounts[0], accounts, 0)

async def show_item_card(callback: types.CallbackQuery, item, all_items: list, page: int):
    """Показ карточки товара"""
    # Цена с наценкой
    lzt_price = item["price"]
    sell_price = round(lzt_price * (1 + config.MARKUP_PERCENT / 100), 2)
    
    text = f"📱 <b>{item.get('title', 'Telegram аккаунт')}</b>\n\n"
    text += f"💰 Цена: {sell_price}₽ (наценка {config.MARKUP_PERCENT}%)\n"
    if item.get("guarantee"):
        text += f"✅ Гарантия: {item['guarantee']}ч\n"
    text += f"\n📝 {item.get('description', 'Описание отсутствует')}"
    
    await callback.message.edit_text(
        text,
        reply_markup=account_kb(item["item_id"], sell_price, page, len(all_items)),
        parse_mode="HTML"
    )
    await callback.answer()