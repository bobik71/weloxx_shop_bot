# core/lzt_client.py
import aiohttp
import asyncio
import time
import logging
from typing import Optional, List, Dict
from urllib.parse import urlencode
import config
from utils.logger import get_logger

# ✅ Инициализируем logger правильно
logger = get_logger(__name__)

class LZTMarketClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = config.LZT_API_BASE
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "TelegramShopBot/1.0"
        }
        self._last_request = 0
        self._min_interval = 60 / config.API_REQUESTS_PER_MIN
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    async def _rate_limit(self):
        now = time.time()
        wait = self._min_interval - (now - self._last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = time.time()

    async def _request(self, method: str, endpoint: str, 
                      params: Dict = None, json_data: Dict = None) -> Optional[Dict]:
        await self._rate_limit()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if params:
            url += "?" + urlencode(params)
        
        for attempt in range(3):
            try:
                async with self._session.request(
                    method, url, headers=self.headers, 
                    json=json_data, timeout=config.API_TIMEOUT
                ) as resp:
                    data = await resp.json() if resp.content_type == "application/json" else {}
                    
                    if resp.status == 200:
                        return data
                    elif resp.status == 401:
                        logger.error(f"❌ 401 Unauthorized: {data}")
                        return None
                    elif resp.status == 403:
                        logger.error(f"❌ 403 Forbidden: {data}")
                        return None
                    elif resp.status == 404:
                        logger.error(f"❌ 404 Not Found: {endpoint}")
                        return None
                    elif resp.status == 429:
                        wait_time = 60 * (attempt + 1)
                        logger.warning(f"⚠️ 429 Rate limit, ждём {wait_time}с...")
                        await asyncio.sleep(wait_time)
                        continue
                    elif resp.status >= 500:
                        logger.error(f"❌ Server error {resp.status}: {data}")
                        return None
                    else:
                        logger.warning(f"⚠️ Status {resp.status}: {data}")
                        return None
            except asyncio.TimeoutError:
                logger.error(f"⏰ Timeout for {endpoint}")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"💥 Error for {endpoint}: {e}")
                await asyncio.sleep(2 ** attempt)
        return None

    # === USER ===
    async def get_balance(self) -> Optional[float]:
        data = await self._request("GET", "/user/money")
        return float(data["balance"]) if data and "balance" in data else None

    async def get_profile(self) -> Optional[Dict]:
        return await self._request("GET", "/user")

    # === MARKET ===
    async def get_categories(self) -> List[str]:
        data = await self._request("GET", "/market/categories")
        if data and "categories" in data:
            return [c["name"].lower() for c in data["categories"] if c.get("name")]
        return []

    async def search_accounts(self, category: str, 
                             price_min: float = None, 
                             price_max: float = None,
                             page: int = 1, 
                             limit: int = 20) -> List[Dict]:
        params = {"page": page, "limit": limit}
        if price_min is not None:
            params["pmin"] = int(price_min)
        if price_max is not None:
            params["pmax"] = int(price_max)
        
        # 🔹 Логирование поиска (исправлено)
        print(f"🔍 Поиск: /market/{category} с параметрами {params}")
        
        data = await self._request("GET", f"/market/{category}", params=params)
        
        if data:
            items = data.get("items", [])
            print(f"✅ Найдено аккаунтов: {len(items)}")
        else:
            print("❌ API не вернул данные")
        
        return data.get("items", []) if data else []

    async def get_account_details(self, item_id: int) -> Optional[Dict]:
        return await self._request("GET", f"/market/item/{item_id}")

    async def buy_account(self, item_id: int, price: float) -> Optional[Dict]:
        """Купить аккаунт на lzt.market"""
        print(f"🛒 Покупка ID={item_id} за {price}₽")
        result = await self._request("POST", f"/market/item/{item_id}/buy", 
                                    json_data={"price": price})
        if result and "item" in result:
            print(f"✅ Покупка успешна!")
            return result
        print(f"❌ Ошибка покупки: {result}")
        return None

    async def check_account(self, item_id: int) -> Optional[Dict]:
        return await self._request("POST", f"/market/item/{item_id}/check")

    async def health_check(self) -> bool:
        try:
            data = await self._request("GET", "/user")
            return data is not None and "username" in data
        except:
            return False