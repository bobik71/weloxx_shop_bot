# core/database.py
import time
import logging
from pathlib import Path
from sqlalchemy import Column, Integer, String, BigInteger, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import config

logger = logging.getLogger(__name__)
Base = declarative_base()

# 📁 Путь к БД
DB_PATH = getattr(config, 'DB_PATH', Path(__file__).parent.parent / "data" / "store.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# 🔌 Подключение
engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_PATH}",
    echo=False,
    future=True
)

# ✅ Правильное создание фабрики сессий
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# 👤 Модель пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    lzt_user_id = Column(Integer, nullable=True)
    lzt_username = Column(String, nullable=True)
    balance = Column(String, default="0")
    created_at = Column(Integer, default=lambda: int(time.time()))

# 📦 Модель заказа
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    lzt_item_id = Column(Integer, nullable=False)
    item_name = Column(String, nullable=False)
    price = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(Integer, default=lambda: int(time.time()))
    paid_at = Column(Integer, nullable=True)

# 🔄 Инициализация
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ База данных инициализирована")

# ✅ Исправленная функция get_db (теперь возвращает сессию напрямую)
async def get_db() -> AsyncSession:
    session = async_session()
    try:
        return session
    finally:
        await session.close()

# 👤 Пользователи
async def get_or_create_user(
    session: AsyncSession, 
    telegram_id: int = None, 
    tg_user = None,
    username: str = None,
    first_name: str = None,
    **kwargs
) -> User:
    if tg_user:
        telegram_id = tg_user.id
        username = tg_user.username
        first_name = getattr(tg_user, 'first_name', first_name)
    elif not telegram_id:
        raise ValueError("Нужно указать либо telegram_id, либо tg_user")
    
    result = await session.execute(select(User).where(User.id == telegram_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        user = User(id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"🆕 Новый пользователь: @{username} (ID: {telegram_id})")
    elif user.username != username:
        user.username = username
        await session.commit()
    
    return user

async def update_lzt_data(session: AsyncSession, tg_user_id: int, lzt_response: dict) -> bool:
    result = await session.execute(select(User).where(User.id == tg_user_id))
    user = result.scalar_one_or_none()
    if user and 'user' in lzt_response:
        data = lzt_response['user']
        user.lzt_user_id = data.get('user_id')
        user.lzt_username = data.get('username')
        user.balance = data.get('balance', '0')
        await session.commit()
        return True
    return False

# 📦 Заказы
async def create_order(session: AsyncSession, user_id: int, lzt_item_id: int, item_name: str, price: str) -> Order:
    order = Order(user_id=user_id, lzt_item_id=lzt_item_id, item_name=item_name, price=price, status="pending")
    session.add(order)
    await session.commit()
    await session.refresh(order)
    logger.info(f"🛒 Заказ #{order.id} создан для пользователя {user_id}")
    return order

async def get_user_orders(session: AsyncSession, user_id: int, limit: int = 10) -> list[Order]:
    result = await session.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(limit)
    )
    return result.scalars().all()

async def update_order_status(session: AsyncSession, order_id: int, status: str, paid_at: int = None) -> bool:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order:
        order.status = status
        if paid_at:
            order.paid_at = paid_at
        await session.commit()
        logger.info(f"📦 Заказ #{order_id} обновлён: {status}")
        return True
    return False

async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    result = await session.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()