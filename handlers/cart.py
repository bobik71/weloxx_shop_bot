# handlers/cart.py
from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from core.lzt_client import LZTMarketClient
from core.payment import CryptoBotPayment
from core.database import create_order
import config

router = Router()
lzt = LZTMarketClient(config.LZT_TOKEN)
payment = CryptoBotPayment()

class PaymentFSM(StatesGroup):
    waiting_payment = State()

@router.callback_query(F.data.startswith("buy_"))
async def start_buy(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    item_id = int(data[1])
    price = float(data[2])
    country_code = data[3] if len(data) > 3 else "US"
    
    state_data = await state.get_data()
    item_info = state_data.get("item_info", {})
    country_name = state_data.get("country_name", "Telegram")
    
    # Находим флаг страны
    country = next((c for c in config.TELEGRAM_ACCOUNTS if c["code"] == country_code), None)
    flag = country["flag"] if country else "📱"
    
    # Создаём счёт
    invoice_data = await payment.create_invoice(
        amount=price,
        description=f"{flag} {country_name} — Telegram аккаунт",
        payload=f"{item_id}_{callback.from_user.id}_{country_code}"
    )
    
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
        f"Нажмите кнопку для оплаты:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💳 Оплатить", url=invoice_url)],
            [types.InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "check_payment", PaymentFSM.waiting_payment)
async def check_payment(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item_id = data.get("item_id")
    price = data.get("price")
    country_code = data.get("country_code")
    country_name = data.get("country_name")
    flag = data.get("flag", "📱")
    invoice_id = data.get("invoice_id")
    
    if not all([item_id, price, invoice_id]):
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Проверяем оплату...")
    
    # Проверяем оплату
    status = await payment.check_invoice(invoice_id)
    
    if status != "paid":
        await callback.message.edit_text(
            f"⏳ Оплата ещё не поступила.\n\n"
            f"Статус: <b>{status}</b>\n\n"
            f"Нажмите «Я оплатил» после оплаты:",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")]
            ]),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Оплата подтверждена — покупаем на lzt
    await callback.message.edit_text("🛒 Покупаем аккаунт...")
    
    # Цена на lzt (без наценки)
    lzt_price = data.get("lzt_price", price * 0.7)
    buy_result = await lzt.buy_account(item_id, lzt_price)
    
    if not buy_result or "item" not in buy_result:
        await callback.message.edit_text(
            "❌ Не удалось купить аккаунт.\n\n"
            f"Средства будут возвращены.\n"
            f"Поддержка: {config.SUPPORT_CHAT}"
        )
        await state.clear()
        return
    
    account_data = buy_result.get("item", {})
    login = account_data.get("login", "N/A")
    password = account_data.get("password", "N/A")
    
    # Сохраняем в БД
    await create_order(
        user_id=callback.from_user.id,
        lzt_item_id=item_id,
        title=f"{flag} {country_name}",
        sell_price=price,
        login=login,
        password=password,
        payment_id=str(invoice_id)
    )
    
    # Выдаём данные
    await callback.message.edit_text(
        f"✅ <b>Покупка успешна!</b>\n\n"
        f"{flag} <b>{country_name}</b>\n\n"
        f"🔑 <b>Логин:</b> <code>{login}</code>\n"
        f"🔐 <b>Пароль:</b> <code>{password}</code>\n\n"
        f"⚠️ <b>Сохраните данные!</b>\n"
        f"🛡️ Гарантия: 24 часа\n"
        f"📞 Поддержка: {config.SUPPORT_CHAT}",
        parse_mode="HTML"
    )
    
    await state.clear()