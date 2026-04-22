# core/payment.py
import aiohttp
import hmac
import hashlib
import config
from utils.logger import get_logger

logger = get_logger(__name__)

class CryptoBotPayment:
    def __init__(self):
        self.token = config.CRYPTOBOT_TOKEN.strip() if config.CRYPTOBOT_TOKEN else ""
        self.testnet = getattr(config, 'CRYPTOBOT_TESTNET', False)
        
        # ✅ Проверка: если токен пустой — не падаем, а предупреждаем
        if not self.token:
            logger.warning("⚠️ CRYPTOBOT_TOKEN не задан. Платежи не будут работать.")
            self.enabled = False
            self.base_url = "https://pay.crypt.bot/api"
            self.headers = {}
        else:
            self.enabled = True
            logger.info("✅ CryptoBot платежи включены")
            logger.info(f"🔑 Токен установлен (длина: {len(self.token)} симв.)")
            self.base_url = "https://testnet.pay.crypt.bot/api" if self.testnet else "https://pay.crypt.bot/api"
            self.headers = {
                "Crypto-Bot-API-Secret": self.token,
                "Content-Type": "application/json"
            }
            logger.debug(f"Base URL: {self.base_url}")
    
    async def create_invoice(self, amount: float, description: str, payload: str, ttl: int = None) -> dict:
        """Создать счёт на оплату
        
        Args:
            amount: Сумма в RUB
            description: Описание платежа
            payload: Данные платежа (до 4000 символов)
            ttl: Время жизни счёта в секундах (опционально)
        """
        if not self.enabled:
            raise RuntimeError("CryptoBot не настроен (CRYPTOBOT_TOKEN не задан в .env)")
        
        json_data = {
            "amount": amount,
            "asset": "RUB",
            "description": description,
            "payload": payload,
            "allow_comments": False,
            "allow_anonymous": False
        }
        
        # Добавляем TTL если указан
        if ttl is not None:
            json_data["ttl"] = ttl
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/createInvoice",
                headers=self.headers,
                json=json_data
            ) as resp:
                # Логируем запрос для отладки
                logger.debug(f"Запрос к CryptoBot: POST {self.base_url}/createInvoice")
                logger.debug(f"Status: {resp.status}")
                
                if resp.status == 401:
                    error_text = await resp.text()
                    logger.error(f"❌ Ошибка авторизации (HTTP 401): {error_text}")
                    logger.error("Проверьте CRYPTOBOT_TOKEN в переменных окружения Railway")
                    logger.error(f"Длина токена: {len(self.token)} симв.")
                    raise RuntimeError(
                        "CryptoBot API вернул ошибку: HTTP 401 (Неверный токен). "
                        "Проверьте значение CRYPTOBOT_TOKEN в настройках Railway."
                    )
                
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"CryptoBot API error: HTTP {resp.status} - {error_text}")
                    raise RuntimeError(f"CryptoBot API вернул ошибку: HTTP {resp.status}")
                
                data = await resp.json()
                
                if not data.get("ok"):
                    error_code = data.get("error", {}).get("code", "unknown")
                    error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
                    logger.error(f"CryptoBot invoice creation failed: {error_code} - {error_msg}")
                    raise RuntimeError(f"Ошибка CryptoBot: {error_msg}")
                
                logger.info(f"✅ Счёт создан успешно: {data.get('result', {}).get('invoice_id', 'N/A')}")
                return data
    
    async def check_invoice(self, invoice_id: int) -> str:
        """Проверить статус счёта"""
        if not self.enabled:
            return "error"
        
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
        if not self.token:
            return False
        
        expected = hmac.new(
            self.token.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)