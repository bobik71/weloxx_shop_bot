# handlers/catalog.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from core.lzt_api import LZTClient  # ✅ Исправлено: LZTClient
from keyboards.catalog_kb import countries_kb, account_kb
import config
router = Router()
lzt = LZTClient()  # ✅ Исправлено: LZTClient

@router.callback_query(F.data == "catalog")
async def show_countries(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📱 <b>Выберите страну:</b>",
        reply_markup=countries_kb(getattr(config, 'TELEGRAM_ACCOUNTS', [])),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("country_"))
async def show_account_for_country(callback: types.CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_", 1)[1]
    
    accounts_list = getattr(config, 'TELEGRAM_ACCOUNTS', [])
    country = next((c for c in accounts_list if c.get("code") == country_code), None)
    
    if not country:
        await callback.answer("⚠️ Страна не найдена", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Ищем аккаунты...")
    
    # ✅ Поиск аккаунтов на lzt.market через API с фильтром по стране
    try:
        # Используем search_query для поиска по префиксу страны (без +)
        # Формат: telegram <код_страны> например: telegram 1 или telegram 44
        prefix = country.get('prefix', '').replace('+', '')
        search_query = f"telegram {prefix}"
        
        items = lzt.get_items(
            search_query=search_query,
            limit=50  # Увеличиваем лимит для большего выбора
        )
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка поиска: {e}")
        await callback.answer()
        return
    
    # Проверяем наличие ошибок в ответе API
    if isinstance(items, dict) and 'errors' in items:
        error_msg = items['errors'][0] if items['errors'] else 'Неизвестная ошибка'
        await callback.message.edit_text(
            f"⚠️ Нет доступных аккаунтов\n\n"
            f"🔑 Ошибка API: {error_msg}\n\n"
            f"Проверьте ваш LZT_TOKEN в .env файле",
            reply_markup=countries_kb(accounts_list)
        )
        await callback.answer()
        return
    
    # Фильтруем товары (если API вернул список)
    accounts = items.get('items', []) if isinstance(items, dict) else items
    
    # Дополнительная фильтрация: проверяем что номер действительно начинается с нужного кода
    filtered_accounts = []
    for acc in accounts:
        title = acc.get('title', '') or acc.get('description', '')
        # Проверяем что в названии есть наш префикс
        if prefix in title or len(prefix) >= 2:  # Для коротких кодов типа +1 более строгая проверка
            filtered_accounts.append(acc)
    
    # Если после фильтрации ничего не осталось, используем оригинальный список
    if filtered_accounts:
        accounts = filtered_accounts[:20]  # Берём первые 20 после фильтрации
    
    if not accounts:
        await callback.message.edit_text(
            f"⚠️ Нет аккаунтов ({country.get('flag', '📱')} {country.get('name', 'Telegram')})\n\n"
            f"Попробуйте другую страну или позже:",
            reply_markup=countries_kb(accounts_list)
        )
        await callback.answer()
        return
    
    # Берём первый доступный
    item = accounts[0]
    
    await state.update_data(
        country_code=country_code,
        country_name=country.get("name", "Telegram"),
        item_id=item.get("item_id") or item.get("id"),
        lzt_price=item.get("price", country.get("price", 100) * 0.7),
        sell_price=country.get("price", 100),
        item_info=item
    )
    
    text = (
        f"{country.get('flag', '📱')} <b>{country.get('name', 'Telegram')}</b>\n\n"
        f"📞 Код: <code>{country.get('prefix', '+1')}</code>\n"
        f"💰 Цена: <b>{country.get('price', 100)}₽</b>\n\n"
        f"📝 {item.get('title') or item.get('description', 'Telegram аккаунт')}\n"
        f"✅ Мгновенная выдача"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=account_kb(item.get("item_id") or item.get("id"), country.get("price", 100), country_code),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "back_countries")
async def back_to_countries(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📱 <b>Выберите страну:</b>",
        reply_markup=countries_kb(getattr(config, 'TELEGRAM_ACCOUNTS', [])),
        parse_mode="HTML"
    )
    await callback.answer()

    