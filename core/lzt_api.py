# core/lzt_api.py
import requests
from config import LZT_TOKEN, MARKET_API_BASE, API_TIMEOUT

class LZTClient:
    def __init__(self):
        self.base_url = MARKET_API_BASE
        self.headers = {
            "Authorization": f"Bearer {LZT_TOKEN}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_me(self):
        """Получить информацию о пользователе"""
        response = self.session.get(f"{self.base_url}/user", timeout=API_TIMEOUT)
        return response.json()
    
    def get_username(self):
        data = self.get_me()
        if data and 'user' in data:
            return data['user'].get('username', 'unknown')
        return 'unknown'
    
    def get_balance(self):
        data = self.get_me()
        if data and 'user' in data:
            return data['user'].get('balance', '0')
        return '0'
    
    def get_balance_value(self):
        data = self.get_me()
        if data and 'user' in data:
            return data['user'].get('convertedBalance', 0)
        return 0
    
    def get_items(self, search_query: str = None, limit: int = 20, page: int = 1):
        """
        Поиск аккаунтов Telegram на lzt.market
        Правильный endpoint: /market/telegram
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        # Добавляем поисковый запрос если указан
        if search_query:
            params["search"] = search_query
        
        # Запрашиваем аккаунты Telegram
        response = self.session.get(
            f"{self.base_url}/market/telegram", 
            params=params, 
            timeout=API_TIMEOUT
        )
        return response.json()
    
    def buy_item(self, item_id: int, price: float = None):
        """Купить аккаунт"""
        data = {}
        if price is not None:
            data["price"] = price
        
        response = self.session.post(
            f"{self.base_url}/market/item/{item_id}/buy", 
            json=data,
            timeout=API_TIMEOUT
        )
        return response.json()
    
    def get_item_info(self, item_id: int):
        """Получить информацию об аккаунте"""
        response = self.session.get(
            f"{self.base_url}/market/item/{item_id}", 
            timeout=API_TIMEOUT
        )
        return response.json()