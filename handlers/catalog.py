# handlers/catalog.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from core.lzt_session import LZTSession
from keyboards.catalog_kb import countries_kb, account_kb
import config

router = Router()
lzt = LZTSession(config.LZT_TOKEN)

@router.callback_query(F.data == "catalog")
async def show_countries(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📱 <b>Выберите страну:</b>",
        reply_markup=countries_kb(config.TELEGRAM_ACCOUNTS),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("country_"))
async def show_account_for_country(callback: types.CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_", 1)[1]
    
    country = next((c for c in config.TELEGRAM_ACCOUNTS if c["code"] == country_code), None)
    if not country:
        await callback.answer("⚠️ Страна не найдена", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Ищем аккаунты...")
    
    # Поиск аккаунтов на lzt.market
    accounts = lzt.search_accounts(
        category="telegram",
        price_min=10,
        price_max=500,
        limit=10
    )
    
    if not accounts:
        await callback.message.edit_text(
            f"⚠️ Нет аккаунтов ({country['flag']} {country['name']})\n\n"
            "Попробуйте позже:",
            reply_markup=countries_kb(config.TELEGRAM_ACCOUNTS)
        )
        await callback.answer()
        return
    
    # Берём первый доступный
    item = accounts[0]
    
    await state.update_data(
        country_code=country_code,
        country_name=country["name"],
        item_id=item.get("item_id") or item.get("id"),
        lzt_price=item.get("price", country["price"] * 0.7),
        sell_price=country["price"],
        item_info=item
    )
    
    text = (
        f"{country['flag']} <b>{country['name']}</b>\n\n"
        f"📞 Код: <code>{country['prefix']}</code>\n"
        f"💰 Цена: <b>{country['price']}₽</b>\n\n"
        f"📝 {item.get('title') or item.get('description', 'Telegram аккаунт')}\n"
        f"✅ Мгновенная выдача"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=account_kb(item.get("item_id") or item.get("id"), country["price"], country_code),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "back_countries")
async def back_to_countries(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📱 <b>Выберите страну:</b>",
        reply_markup=countries_kb(config.TELEGRAM_ACCOUNTS),
        parse_mode="HTML"
    )
    await callback.answer()