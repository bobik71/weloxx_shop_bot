# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager
from datetime import datetime
from .models import Base, User, Account, Order, CartItem, PaymentLog
from cryptography.fernet import Fernet
import json, config
from utils.logger import get_logger

logger = get_logger(__name__)
engine = create_async_engine(f"sqlite+aiosqlite:///{config.DB_PATH}", echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)
fernet = Fernet(config.ENCRYPTION_KEY.encode())

@asynccontextmanager
async def get_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"DB Error: {e}")
            raise

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def encrypt(data: str) -> str: 
    return fernet.encrypt(data.encode()).decode()

def decrypt(data: str) -> str: 
    return fernet.decrypt(data.encode()).decode()

# === USER ===
# ✅ ИСПРАВЛЕНО: telegram_id вместо tg_id
async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None):
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            session.add(user)
            logger.info(f"🆕 Новый пользователь: {telegram_id}")
        return user

async def get_user_by_id(telegram_id: int):
    async with get_session() as session:
        return await session.get(User, telegram_id)

# === ACCOUNT ===
async def add_account(lzt_id: int, category: str, title: str, price: float,
                     login: str, password: str, description: str = "",
                     guaranteed: bool = False, guarantee_h: int = 0):
    async with get_session() as session:
        acc = Account(
            lzt_item_id=lzt_id, category=category.lower(), title=title,
            description=description, price=price,
            login_encrypted=encrypt(login), password_encrypted=encrypt(password),
            is_guaranteed=guaranteed, guarantee_hours=guarantee_h
        )
        session.add(acc)
        return acc

async def get_accounts(category: str = None, pmin: float = None, pmax: float = None, limit: int = 20):
    async with get_session() as session:
        q = select(Account).where(Account.is_available == True)
        if category: q = q.where(Account.category == category.lower())
        if pmin: q = q.where(Account.price >= pmin)
        if pmax: q = q.where(Account.price <= pmax)
        q = q.order_by(Account.added_at.desc()).limit(limit)
        return (await session.execute(q)).scalars().all()

async def get_account(aid: int):
    async with get_session() as session: 
        return await session.get(Account, aid)

async def mark_sold(aid: int):
    async with get_session() as session:
        await session.execute(update(Account).where(Account.id == aid).values(is_available=False))

# === CART ===
async def add_to_cart(uid: int, aid: int):
    async with get_session() as session:
        if await session.scalar(select(CartItem).where(CartItem.user_id==uid, CartItem.account_id==aid)):
            return False
        session.add(CartItem(user_id=uid, account_id=aid))
        return True

async def get_cart(uid: int):
    async with get_session() as session:
        return (await session.execute(
            select(CartItem).options(selectinload(CartItem.account)).where(CartItem.user_id==uid)
        )).scalars().all()

async def clear_cart(uid: int):
    async with get_session() as session:
        await session.execute(delete(CartItem).where(CartItem.user_id==uid))

# === ORDER ===
async def create_order(uid: int, aid: int, method: str, amount: float):
    async with get_session() as session:
        order = Order(user_id=uid, account_id=aid, payment_method=method, amount_paid=amount)
        session.add(order)
        await session.flush()
        return order

async def update_order(oid: int, status: str, pay_id: str = None):
    async with get_session() as session:
        vals = {"status": status}
        if pay_id: vals["payment_id"] = pay_id
        if status == "completed": vals["completed_at"] = datetime.utcnow()
        await session.execute(update(Order).where(Order.id==oid).values(**vals))