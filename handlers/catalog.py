# handlers/catalog.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from core.lzt_client import LZTMarketClient
from keyboards.catalog_kb import countries_kb, account_kb
import config

router = Router()
lzt = LZTMarketClient(config.LZT_TOKEN)

@router.callback_query(F.data == "catalog")
async def show_countries(callback: types.CallbackQuery, state: FSMContext):
    """Показываем список стран"""
    await callback.message.edit_text(
        "📱 <b>Выберите страну:</b>\n\n"
        "Цены актуальны на данный момент:",
        reply_markup=countries_kb(config.TELEGRAM_ACCOUNTS),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("country_"))
async def show_account_for_country(callback: types.CallbackQuery, state: FSMContext):
    """Поиск аккаунта для выбранной страны"""
    country_code = callback.data.split("_", 1)[1]
    
    # Находим информацию о стране
    country = next((c for c in config.TELEGRAM_ACCOUNTS if c["code"] == country_code), None)
    if not country:
        await callback.answer("⚠️ Страна не найдена", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Ищем доступные аккаунты...")
    
    # Ищем Telegram аккаунты на lzt.market
    accounts = await lzt.search_accounts(
        category="telegram",
        price_min=30,
        price_max=200,
        limit=5
    )
    
    if not accounts:
        await callback.message.edit_text(
            f"⚠️ Временно нет аккаунтов ({country['flag']} {country['name']})\n\n"
            "Попробуйте позже или выберите другую страну:",
            reply_markup=countries_kb(config.TELEGRAM_ACCOUNTS)
        )
        return
    
    # Берём первый доступный аккаунт
    item = accounts[0]
    
    # Сохраняем в состояние
    await state.update_data(
        country_code=country_code,
        country_name=country["name"],
        item_id=item["item_id"],
        lzt_price=item["price"],
        sell_price=country["price"],
        item_info=item
    )
    
    # Показываем карточку товара
    text = (
        f"{country['flag']} <b>{country['name']}</b>\n\n"
        f"📞 Код: <code>{country['prefix']}</code>\n"
        f"💰 Цена: <b>{country['price']}₽</b>\n\n"
        f"📝 {item.get('description', 'Telegram аккаунт')}\n\n"
        f"✅ Мгновенная выдача\n"
        f"🛡️ Гарантия: 24 часа"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=account_kb(item["item_id"], country["price"], country_code),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "back_countries")
async def back_to_countries(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку стран"""
    await state.clear()
    await callback.message.edit_text(
        "📱 <b>Выберите страну:</b>",
        reply_markup=countries_kb(config.TELEGRAM_ACCOUNTS),
        parse_mode="HTML"
    )
    await callback.answer()