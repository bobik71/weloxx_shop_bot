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

    def get_items(self, search_query: str = None, limit: int = 20, price_min: float = None, price_max: float = None) -> dict:
        """
        Поиск товаров на lzt.market
        
        :param search_query: Поисковый запрос (например, код страны)
        :param limit: Количество результатов
        :param price_min: Минимальная цена
        :param price_max: Максимальная цена
        :return: dict с результатами поиска
        """
        params = {
            "page": 1,
            "limit": limit
        }
        
        if search_query:
            params["search"] = search_query
        if price_min is not None:
            params["pmin"] = int(price_min)
        if price_max is not None:
            params["pmax"] = int(price_max)
        
        try:
            # Поиск аккаунтов Telegram
            endpoint = f"{self.base_url}/market/telegram"
            logger.info(f"🔍 Поиск: {endpoint} с параметрами {params}")
            
            resp = self.session.get(endpoint, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            
            if data:
                items = data.get("items", [])
                logger.info(f"✅ Найдено аккаунтов: {len(items)}")
            else:
                logger.warning("❌ API не вернул данные")
            
            return data
        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass
            logger.error(f"❌ LZT API HTTP {e.response.status_code}: {error_data}")
            return {"errors": [f"HTTP {e.response.status_code}: {error_data}"]}
        except Exception as e:
            logger.error(f"❌ LZT API ошибка поиска: {type(e).__name__}: {e}")
            return {"errors": [str(e)]}

    def get_account_details(self, item_id: int) -> dict:
        """Получить детали аккаунта по ID"""
        try:
            resp = self.session.get(f"{self.base_url}/market/item/{item_id}", timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"❌ Ошибка получения деталей аккаунта {item_id}: {e}")
            return {"errors": [str(e)]}

    def buy_account(self, item_id: int, price: float) -> dict:
        """Купить аккаунт на lzt.market"""
        logger.info(f"🛒 Покупка ID={item_id} за {price}₽")
        try:
            resp = self.session.post(
                f"{self.base_url}/market/item/{item_id}/buy",
                json={"price": price},
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            if "item" in data:
                logger.info("✅ Покупка успешна!")
            return data
        except Exception as e:
            logger.error(f"❌ Ошибка покупки {item_id}: {e}")
            return {"errors": [str(e)]}