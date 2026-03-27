import aiohttp
import asyncio
import time
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode
import config
from utils.logger import get_logger

logger = get_logger(__name__)

class LZTMarketClient:
    """Клиент для API lzt.market (актуальные эндпоинты)"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = config.LZT_API_BASE  # https://lzt.market/api/v1
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "LZTStoreBot/1.0"
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
                        logger.error("❌ 401: Неверный токен")
                        return None
                    elif resp.status == 404:
                        logger.error(f"❌ 404: {endpoint}")
                        return None
                    elif resp.status == 429:
                        await asyncio.sleep(60 * (attempt + 1))
                        continue
                    else:
                        logger.warning(f"⚠️ {resp.status}: {data}")
                        return None
            except Exception as e:
                logger.error(f"💥 Ошибка запроса: {e}")
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
        return [c["name"].lower() for c in data.get("categories", []) if c.get("name")] if data else []

    async def search_accounts(self, category: str, query: str = None,
                           price_min: float = None, price_max: float = None,
                           page: int = 1, limit: int = 20) -> List[Dict]:
        params = {"page": page, "limit": limit}
        if query: params["title"] = query
        if price_min: params["pmin"] = int(price_min)
        if price_max: params["pmax"] = int(price_max)
        data = await self._request("GET", f"/market/{category}", params=params)
        return data.get("items", []) if data else []

    async def get_account_details(self, item_id: int) -> Optional[Dict]:
        return await self._request("GET", f"/market/item/{item_id}")

    async def check_account(self, item_id: int) -> Optional[Dict]:
        return await self._request("POST", f"/market/item/{item_id}/check")

    async def buy_account(self, item_id: int, price: float) -> Optional[Dict]:
        return await self._request("POST", f"/market/item/{item_id}/buy", json_data={"price": price})