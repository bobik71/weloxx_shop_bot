# core/payment.py
import aiohttp
import hmac
import hashlib
import config
from utils.logger import get_logger

logger = get_logger(__name__)

class CryptoBotPayment:
    def __init__(self):
        self.token = config.CRYPTOBOT_TOKEN
        self.testnet = config.CRYPTOBOT_TESTNET
        self.base_url = "https://testnet.pay.crypt.bot/api" if self.testnet else "https://pay.crypt.bot/api"
        self.headers = {
            "Crypto-Bot-API-Secret": self.token,
            "Content-Type": "application/json"
        }
    
    async def create_invoice(self, amount: float, description: str, payload: str) -> dict:
        """Создать счёт на оплату"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/createInvoice",
                headers=self.headers,
                json={
                    "amount": amount,
                    "asset": "RUB",
                    "description": description,
                    "payload": payload,
                    "allow_comments": False,
                    "allow_anonymous": False
                }
            ) as resp:
                return await resp.json()
    
    async def check_invoice(self, invoice_id: int) -> str:
        """Проверить статус счёта"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/getInvoices",
                headers=self.headers,
                json={"invoice_ids": [invoice_id]}
            ) as resp:
                data = await resp.json()
                invoices = data.get("result", [])
                return invoices[0].get("status", "unknown") if invoices else "unknown"
    
    def verify_webhook(self, body: str, signature: str) -> bool:
        """Проверить подпись вебхука"""
        expected = hmac.new(
            self.token.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
# core/payment.py
import config
import logging

logger = logging.getLogger(__name__)

class CryptoBotPayment:
    def __init__(self):
        self.token = config.CRYPTOBOT_TOKEN
        
        # ✅ Проверка: если токен пустой — не падаем, а предупреждаем
        if not self.token:
            logger.warning("⚠️ CRYPTOBOT_TOKEN не задан. Платежи не будут работать.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ CryptoBot платежи включены")
    
    async def create_invoice(self, amount: float, description: str) -> str:
        """Создаёт счёт на оплату"""
        if not self.enabled:
            raise RuntimeError("CryptoBot не настроен")
        
        # ... ваш код создания инвойса ...
        pass
    
    async def check_payment(self, invoice_id: str) -> bool:
        """Проверяет статус оплаты"""
        if not self.enabled:
            return False
        
        # ... ваш код проверки ...
        pass