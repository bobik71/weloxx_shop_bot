import requests
from config import LZT_TOKEN, LZT_BASE_URL, API_TIMEOUT
import logging

logger = logging.getLogger(__name__)

class LZTClient:  # ✅ Имя как в оригинале
    def __init__(self):
        self.token = LZT_TOKEN
        self.base_url = LZT_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "WeloxxShopBot/1.0"
        })

    def check_connection(self) -> dict:
        try:
            resp = self.session.get(f"{self.base_url}/me", timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "username": data.get("username") or data.get("login", "unknown"),
                "balance": data.get("balance", 0)
            }
        except Exception as e:
            logger.error(f"Ошибка проверки LZT API: {e}")
            return {"success": False, "username": "unknown", "balance": 0}

    def get_telegram_accounts(self, limit: int = 20, page: int = 1, search_query: str = None):
        try:
            params = {"limit": limit, "page": page}
            if search_query:
                params["title"] = search_query

            url = f"{self.base_url}/telegram"  # ✅ Без /market/
            resp = self.session.get(url, params=params, timeout=API_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Ошибка получения аккаунтов: {e}")
            return {"items": [], "total": 0}

    def buy_item(self, item_id: int) -> dict:
        """Купить аккаунт на lzt.market"""
        try:
            url = f"{self.base_url}/telegram/{item_id}/buy"
            resp = self.session.post(url, timeout=API_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Ошибка покупки аккаунта {item_id}: {e}")
            return {"errors": [str(e)]}

    def get_account_info(self, item_id: int):
        try:
            url = f"{self.base_url}/telegram/{item_id}"
            resp = self.session.get(url, timeout=API_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Ошибка получения инфо о лоте {item_id}: {e}")
            return None

    # 🔗 Совместимость со старым кодом хендлеров
    get_items = get_telegram_accounts
    get_item_info = get_account_info
    buy_item = buy_item