# handlers/cart.py
from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from core.lzt_api import LZTClient
from core.payment import CryptoBotPayment
from core.database import create_order, get_db
import config

router = Router()
lzt = LZTClient()
payment = CryptoBotPayment()

class PaymentFSM(StatesGroup):
    waiting_payment = State()

@router.callback_query(F.data.startswith("buy_"))
async def start_buy(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    item_id = int(parts[1])
    price = float(parts[2])
    country_code = parts[3] if len(parts) > 3 else "US"
    
    state_data = await state.get_data()
    item_info = state_data.get("item_info", {})
    country_name = state_data.get("country_name", "Telegram")
    
    country = next((c for c in getattr(config, 'TELEGRAM_ACCOUNTS', []) if c.get("code") == country_code), None)
    flag = country.get("flag") if country else "📱"
    
    # Создаём счёт CryptoBot
    try:
        invoice_data = await payment.create_invoice(
            amount=price,
            description=f"{flag} {country_name} — Telegram",
            payload=f"{item_id}_{callback.from_user.id}_{country_code}"
        )
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка создания счёта: {e}")
        return
    
    if not invoice_data or not invoice_data.get("ok"):
        await callback.message.edit_text("❌ Ошибка создания счёта.")
        return
    
    invoice_id = invoice_data["result"]["invoice_id"]
    invoice_url = invoice_data["result"]["invoice_url"]
    
    await state.update_data(
        item_id=item_id,
        price=price,
        country_code=country_code,
        country_name=country_name,
        flag=flag,
        invoice_id=invoice_id
    )
    await state.set_state(PaymentFSM.waiting_payment)
    
    await callback.message.edit_text(
        f"💳 <b>Оплата</b>\n\n"
        f"Товар: {flag} {country_name}\n"
        f"Сумма: <b>{price}₽</b>\n\n"
        f"[💳 Оплатить]({invoice_url})",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")]
        ]),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "check_payment", PaymentFSM.waiting_payment)
async def check_payment(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item_id = data.get("item_id")
    price = data.get("price")
    country_name = data.get("country_name")
    flag = data.get("flag", "📱")
    invoice_id = data.get("invoice_id")
    
    if not all([item_id, price, invoice_id]):
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Проверяем оплату...")
    
    # Проверка оплаты
    try:
        status = await payment.check_invoice(invoice_id)
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка проверки оплаты: {e}")
        await state.clear()
        return
    
    if status != "paid":
        await callback.message.edit_text(
            f"⏳ Оплата не подтверждена.\n"
            f"Статус: <b>{status}</b>\n\n"
            f"Нажмите «Я оплатил» после оплаты:",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")]
            ]),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # ✅ Оплата подтверждена — покупаем на lzt.market
    await callback.message.edit_text("🛒 Покупаем аккаунт на lzt.market...")
    
    # Попытка купить через API
    try:
        buy_result = lzt.buy_item(item_id)
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка покупки: {e}")
        await state.clear()
        return
    
    # Проверяем ответ API
    if not buy_result:
        await callback.message.edit_text(
            "❌ Не удалось купить аккаунт.\n"
            f"Поддержка: {getattr(config, 'SUPPORT_CHAT', '@support')}"
        )
        await state.clear()
        return
    
    # Проверяем наличие ошибок в ответе API
    if isinstance(buy_result, dict):
        if 'errors' in buy_result and buy_result['errors']:
            error_msg = buy_result['errors'][0] if isinstance(buy_result['errors'], list) else str(buy_result['errors'])
            await callback.message.edit_text(
                f"❌ Ошибка при покупке:\n{error_msg}\n\n"
                f"Возможно, аккаунт уже куплен или недостаточно средств.\n"
                f"Поддержка: {getattr(config, 'SUPPORT_CHAT', '@support')}"
            )
            await state.clear()
            return
        
        # Получаем данные аккаунта из ответа
        account_data = buy_result.get('item', {}) or buy_result
    else:
        account_data = {}
    
    login = account_data.get('login') or account_data.get('username') or "N/A"
    password = account_data.get('password') or account_data.get('pass') or "N/A"
    
    # ✅ Сохраняем в БД (с сессией!)
    session = await get_db()
    try:
        await create_order(
            session=session,
            user_id=callback.from_user.id,
            lzt_item_id=item_id,
            item_name=f"{flag} {country_name}",
            price=str(price)
        )
    finally:
        await session.close()
    
    # Выдача данных клиенту
    await callback.message.edit_text(
        f"✅ <b>Покупка успешна!</b>\n\n"
        f"{flag} <b>{country_name}</b>\n\n"
        f"🔑 <b>Логин:</b> <code>{login}</code>\n"
        f"🔐 <b>Пароль:</b> <code>{password}</code>\n\n"
        f"⚠️ <b>Сохраните данные!</b>\n"
        f"🛡️ Гарантия: 24 часа",
        parse_mode="HTML"
    )
    
    await state.clear()