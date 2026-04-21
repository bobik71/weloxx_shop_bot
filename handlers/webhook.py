# handlers/webhook.py — Обработчик вебхуков CryptoBot
from aiogram import Router, F, types
from core.payment import CryptoBotPayment
from core.database import get_db, update_order_status
from sqlalchemy import select
from core.database import Order as DBOrder
import time
import logging

logger = logging.getLogger(__name__)

# ✅ ИСПРАВЛЕНИЕ: Создаём и экспортируем router для совместимости с handlers/__init__.py
router = Router(name="webhook")

payment = CryptoBotPayment()

@router.callback_query(F.data == "webhook_test")
async def webhook_test_callback(callback: types.CallbackQuery):
    """Тестовый хендлер для проверки работы роутера"""
    await callback.answer("✅ Webhook router работает!", show_alert=True)

async def process_cryptobot_webhook(data: dict):
    """
    Логика обработки вебхука от CryptoBot
    Вызывается из отдельного HTTP-сервера (не через aiogram)
    """
    if not payment.enabled:
        logger.warning("⚠️ Вебхук получен, но CryptoBot не настроен")
        return {"status": "error"}

    invoice_id = data.get('invoice_id')
    status = data.get('status')
    payload = data.get('payload', '')

    logger.info(f"📬 Вебхук от CryptoBot: invoice_id={invoice_id}, status={status}")

    if status != 'paid':
        logger.info(f"⏳ Оплата ещё не подтверждена: {status}")
        return {"status": "ok"}

    # Извлекаем данные из payload: "{item_id}_{user_id}_{country_code}"
    try:
        parts = payload.split('_')
        item_id = int(parts[0])
        user_id = int(parts[1])
        country_code = parts[2] if len(parts) > 2 else "US"
    except (ValueError, IndexError) as e:
        logger.error(f"❌ Ошибка парсинга payload '{payload}': {e}")
        return {"status": "error"}

    # Находим заказ в БД по item_id и user_id
    session = await get_db()
    try:
        result = await session.execute(
            select(DBOrder)
            .where(DBOrder.user_id == user_id)
            .where(DBOrder.lzt_item_id == item_id)
            .where(DBOrder.status == 'pending')
            .order_by(DBOrder.created_at.desc())
            .limit(1)
        )
        order = result.scalar_one_or_none()

        if not order:
            logger.warning(f"⚠️ Заказ не найден: user_id={user_id}, item_id={item_id}")
            return {"status": "ok"}

        # Обновляем статус заказа
        await update_order_status(
            session=session,
            order_id=order.id,
            status='paid',
            paid_at=int(time.time())
        )

        logger.info(f"✅ Заказ #{order.id} помечен как оплаченный (вебхук)")
        return {"status": "ok"}

    finally:
        await session.close()