# core/lzt_api.py
import requests
import logging
from config import LZT_TOKEN, LZT_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

class LZTClient:
    def __init__(self):
        # ✅ Гарантируем строку без лишних символов
        self.token = str(LZT_TOKEN).strip()
        self.base_url = str(LZT_BASE_URL).strip()
        self.timeout = int(API_TIMEOUT)  # ✅ Гарантируем int

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "WeloxxShopBot/1.0"
        })

    def check_connection(self) -> dict:
        try:
            resp = self.session.get(f"{self.base_url}/me", timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "username": data.get("username", "unknown"),
                "balance": data.get("balance", 0)
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ LZT API HTTP {e.response.status_code if e.response else '?'}: {e}")
        except Exception as e:
            logger.error(f"❌ LZT API ошибка: {type(e).__name__}: {e}")
        return {"success": False, "username": "unknown", "balance": 0}

    # Добавьте остальные методы (get_items, buy_item и т.д.) по аналогии,
    # обязательно передавая timeout=self.timeout и проверяя типы параметров.