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
    price = float(data[2]) if len(data) > 2 else 0
    
    state_data = await state.get_data()
    items = state_data.get("items", {})
    item_info = items.get(str(item_id), {})
    
    if not item_info:
        await callback.answer("⚠️ Товар не найден", show_alert=True)
        return
    
    # Создаём счёт
    invoice_data = await payment.create_invoice(
        amount=price,
        description=f"📱 Telegram аккаунт: {item_info.get('title', 'N/A')}",
        payload=f"{item_id}_{callback.from_user.id}"
    )
    
    if not invoice_data or not invoice_data.get("ok"):
        await callback.message.edit_text("❌ Ошибка создания счёта.")
        return
    
    invoice_id = invoice_data["result"]["invoice_id"]
    invoice_url = invoice_data["result"]["invoice_url"]
    
    await state.update_data(
        item_id=item_id,
        price=price,
        item_info=item_info,
        invoice_id=invoice_id
    )
    await state.set_state(PaymentFSM.waiting_payment)
    
    await callback.message.edit_text(
        f"💳 <b>Оплата</b>\n\n"
        f"Товар: 📱 {item_info.get('title', 'Telegram аккаунт')}\n"
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
    item_info = data.get("item_info")
    invoice_id = data.get("invoice_id")
    
    if not all([item_id, price, item_info, invoice_id]):
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
    
    lzt_price = item_info.get("price", price * 0.8)
    buy_result = await lzt.buy_account(item_id, lzt_price)
    
    if not buy_result or "item" not in buy_result:
        await callback.message.edit_text(
            "❌ Не удалось купить аккаунт.\n\n"
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
        title=item_info.get("title", "Telegram аккаунт"),
        sell_price=price,
        login=login,
        password=password,
        payment_id=str(invoice_id)
    )
    
    # Выдаём данные
    await callback.message.edit_text(
        f"✅ <b>Покупка успешна!</b>\n\n"
        f"📱 {item_info.get('title', 'Telegram аккаунт')}\n\n"
        f"🔑 <b>Логин:</b> <code>{login}</code>\n"
        f"🔐 <b>Пароль:</b> <code>{password}</code>\n\n"
        f"⚠️ <b>Сохраните данные!</b>\n"
        f"Гарантия: 24 часа\n"
        f"Поддержка: {config.SUPPORT_CHAT}",
        parse_mode="HTML"
    )
    
    await state.clear()

# 🔹 Заглушки для будущих команд
@router.callback_query(F.data == "orders")
async def show_orders(callback: types.CallbackQuery):
    await callback.answer("📚 История покупок скоро будет!", show_alert=True)

@router.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    await callback.answer(
        f"📞 Поддержка: {config.SUPPORT_CHAT}\n"
        f"⏱️ Гарантия: 24 часа",
        show_alert=True
    )