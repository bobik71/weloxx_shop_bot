# core/lzt_session.py
import requests
import json
import time
import config
from utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)

class LZTSession:
    """Класс для запросов к lzt.market с куки из файла"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://lzt.market"
        self.session = requests.Session()
        
        # Заголовки как у браузера
        self.headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Referer": "https://lzt.market/",
            "Origin": "https://lzt.market",
        }
        
        # Загружаем куки из файла
        self._load_cookies_from_file()
    
    def _load_cookies_from_file(self):
        """Загружает куки из JSON файла"""
        cookie_file = Path("lzt_cookies.json")
        
        if not cookie_file.exists():
            logger.error("❌ Файл lzt_cookies.json не найден!")
            logger.error("💡 Запустите export_cookies.py на домашнем ПК и загрузите файл на сервер")
            return
        
        try:
            with open(cookie_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            
            for c in cookies:
                self.session.cookies.set(
                    name=c["name"],
                    value=c["value"],
                    domain=c.get("domain", ".lzt.market"),
                    path=c.get("path", "/")
                )
            
            logger.info(f"✅ Загружено {len(cookies)} куки из файла")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки куки: {e}")
    
    def _request(self, method: str, endpoint: str, params: dict = None, json_data: dict = None) -> dict:
        """Базовый метод запроса"""
        url = f"{self.base_url}{endpoint}"
        
        # Задержка между запросами
        time.sleep(1)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json_data,
                timeout=30
            )
            
            content_type = response.headers.get("Content-Type", "")
            
            if "application/json" in content_type:
                return response.json()
            elif response.status_code == 200:
                try:
                    return json.loads(response.text)
                except:
                    return {"error": "Invalid response format"}
            else:
                logger.error(f"❌ Ошибка {response.status_code}: {response.text[:200]}")
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"💥 Ошибка запроса: {e}")
            return {"error": str(e)}
    
    # === ПУБЛИЧНЫЕ МЕТОДЫ ===
    
    def get_balance(self) -> float:
        """Получить баланс"""
        data = self._request("GET", "/api/v1/user/money")
        return data.get("balance", 0) if "balance" in data else 0
    
    def search_accounts(self, category: str, price_min: float = None, price_max: float = None, limit: int = 20) -> list:
        """Поиск аккаунтов"""
        params = {"limit": limit}
        if price_min: params["pmin"] = int(price_min)
        if price_max: params["pmax"] = int(price_max)
        
        data = self._request("GET", f"/api/v1/market/{category}", params=params)
        
        if "items" in data:
            return data["items"]
        elif isinstance(data, list):
            return data
        return []
    
    def buy_account(self, item_id: int, price: float) -> dict:
        """Купить аккаунт"""
        logger.info(f"🛒 Покупка аккаунта #{item_id} за {price}₽")
        
        data = self._request("POST", f"/api/v1/market/item/{item_id}/buy", json_data={"price": price})
        
        if "item" in data or "success" in data:
            logger.info(f"✅ Покупка успешна!")
            return data
        logger.error(f"❌ Ошибка покупки: {data}")
        return data
    
    def health_check(self) -> bool:
        """Проверка работоспособности"""
        try:
            data = self._request("GET", "/api/v1/user")
            return "username" in data or "id" in data
        except:
            return False