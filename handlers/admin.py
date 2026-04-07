# handlers/admin.py
from aiogram import Router, F, types, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import config

router = Router()

class AddAccountFSM(StatesGroup):
    category = State()
    title = State()
    price = State()
    login = State()
    password = State()
    description = State()

@router.message(F.command == "admin")
async def cmd_admin(msg: types.Message):
    if msg.from_user.id not in config.ADMIN_IDS:
        return await msg.answer("⛔ Доступ запрещён")
    from keyboards.main_kb import back_kb
    kb = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="➕ Добавить аккаунт")],
        [types.KeyboardButton(text="🔙 Меню")]
    ], resize_keyboard=True)
    await msg.answer("⚙️ <b>Админ-панель</b>", reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "➕ Добавить аккаунт")
async def start_add(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in config.ADMIN_IDS: return
    await state.set_state(AddAccountFSM.category)
    await msg.answer("📁 Введите категорию (steam, vk, epic...):")

@router.message(AddAccountFSM.category)
async def set_cat(msg: types.Message, state: FSMContext):
    await state.update_data(category=msg.text.lower().strip())
    await state.set_state(AddAccountFSM.title)
    await msg.answer("🏷️ Введите название товара:")

@router.message(AddAccountFSM.title)
async def set_title(msg: types.Message, state: FSMContext):
    await state.update_data(title=msg.text.strip())
    await state.set_state(AddAccountFSM.price)
    await msg.answer("💰 Введите цену в рублях:")

@router.message(AddAccountFSM.price)
async def set_price(msg: types.Message, state: FSMContext):
    try: price = float(msg.text)
    except: return await msg.answer("❌ Неверная цена")
    await state.update_data(price=price)
    await state.set_state(AddAccountFSM.login)
    await msg.answer("🔑 Введите логин аккаунта:")

@router.message(AddAccountFSM.login)
async def set_login(msg: types.Message, state: FSMContext):
    await state.update_data(login=msg.text.strip())
    await state.set_state(AddAccountFSM.password)
    await msg.answer("🔐 Введите пароль аккаунта:")

@router.message(AddAccountFSM.password)
async def set_pass(msg: types.Message, state: FSMContext):
    await state.update_data(password=msg.text.strip())
    await state.set_state(AddAccountFSM.description)
    await msg.answer("📝 Введите описание (или пропустите):")

@router.message(AddAccountFSM.description)
async def finish_add(msg: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    desc = msg.text.strip() if msg.text != "пропустить" else ""
    await state.clear()
    await msg.answer(
        f"ℹ️ Функция добавления аккаунтов через бота временно отключена.\n\n"
        f"✅ Аккаунт '{data['title']}' будет добавлен вручную администратором.",
        parse_mode="HTML"
    )
    # Уведомить админов
    for aid in config.ADMIN_IDS:
        if aid:
            try:
                await bot.send_message(aid, f"📦 Запрос на добавление аккаунта: {data['title']}")
            except:
                pass