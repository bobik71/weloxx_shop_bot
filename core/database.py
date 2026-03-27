# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from contextlib import asynccontextmanager
from datetime import datetime
from .models import Base, User, Order
from cryptography.fernet import Fernet
import config
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
async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None):
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            session.add(user)
        return user

# === ORDER ===
async def create_order(user_id: int, lzt_item_id: int, title: str,
                      sell_price: float, login: str, password: str,
                      payment_id: str = None):
    async with get_session() as session:
        order = Order(
            user_id=user_id,
            lzt_item_id=lzt_item_id,
            title=title,
            sell_price=sell_price,
            login_encrypted=encrypt(login),
            password_encrypted=encrypt(password),
            payment_id=payment_id,
            status="completed"
        )
        session.add(order)
        await session.flush()
        return order

async def get_user_orders(user_id: int, limit: int = 10):
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()