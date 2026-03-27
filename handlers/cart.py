from aiogram import Router, F, types
from core.database import get_cart, clear_cart, create_order, update_order, mark_sold, decrypt, get_account
import config

router = Router()

@router.callback_query(F.data == "cart")
async def show_cart(cb: types.CallbackQuery):
    items = await get_cart(cb.from_user.id)
    if not items:
        await cb.answer("🛒 Корзина пуста", show_alert=True)
        return
    text = "🛒 <b>Ваша корзина:</b>\n\n"
    total = 0
    for item in items:
        text += f"• {item.account.title} — {item.account.price}₽\n"
        total += item.account.price
    text += f"\n💰 Итого: {total}₽"
    from keyboards.main_kb import back_kb
    await cb.message.edit_text(text, reply_markup=back_kb("main_menu"), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data.startswith("buy_"))
async def buy_now(cb: types.CallbackQuery):
    aid = int(cb.data.split("_")[-1])
    acc = await get_account(aid)
    if not acc or not acc.is_available:
        await cb.answer("⚠️ Товар недоступен", show_alert=True)
        return
    
    # ТЕСТОВЫЙ РЕЖИМ: сразу выдаём
    login = decrypt(acc.login_encrypted)
    password = decrypt(acc.password_encrypted)
    
    await cb.message.answer(
        f"✅ <b>Покупка успешна!</b>\n\n"
        f"🎮 {acc.title}\n"
        f"🔑 Логин: <code>{login}</code>\n"
        f"🔐 Пароль: <code>{password}</code>\n\n"
        f"⚠️ Сохраните данные! Гарантия: {acc.guarantee_hours}ч",
        parse_mode="HTML"
    )
    await mark_sold(aid)
    await clear_cart(cb.from_user.id)
    await cb.answer()