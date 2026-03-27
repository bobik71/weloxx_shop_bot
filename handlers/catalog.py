from aiogram import Router, F, types
from core.database import get_accounts, get_cart, add_to_cart, get_account
from core.lzt_client import LZTMarketClient
from keyboards.catalog_kb import categories_kb, account_kb
import config

router = Router()
lzt = LZTMarketClient(config.LZT_TOKEN)

@router.callback_query(F.data == "catalog")
async def show_cats(cb: types.CallbackQuery):
    cats = await lzt.get_categories()
    popular = [c for c in cats if c in ["steam","vk","epic","origin","uplay","discord"]]
    await cb.message.edit_text("🎮 Выберите категорию:", reply_markup=categories_kb(popular or cats))
    await cb.answer()

@router.callback_query(F.data.startswith("cat_"))
async def show_items(cb: types.CallbackQuery):
    cat = cb.data.split("_",1)[1]
    accounts = await get_accounts(category=cat, limit=10)
    if not accounts:
        await cb.answer("⚠️ Нет аккаунтов", show_alert=True)
        return
    await show_card(cb, accounts[0], accounts, cat, 0)

async def show_card(cb: types.CallbackQuery, acc, all_accs: list, cat: str, page: int):
    cart = await get_cart(cb.from_user.id)
    in_cart = any(c.account_id == acc.id for c in cart)
    text = f"🎮 <b>{acc.title}</b>\n\n💰 {acc.price} {acc.currency}"
    if acc.is_guaranteed: text += f"\n✅ Гарантия: {acc.guarantee_hours}ч"
    text += f"\n\n📝 {acc.description or 'Описание отсутствует'}"
    await cb.message.edit_text(text, reply_markup=account_kb(acc.id, in_cart), parse_mode="HTML")
    await cb.answer()
    await cb.state.update_data(category=cat, accounts=[a.id for a in all_accs], page=page)

@router.callback_query(F.data.startswith("add_"))
async def add_cart(cb: types.CallbackQuery):
    aid = int(cb.data.split("_")[-1])
    ok = await add_to_cart(cb.from_user.id, aid)
    await cb.answer("✅ Добавлено!" if ok else "⚠️ Уже в корзине", show_alert=True)