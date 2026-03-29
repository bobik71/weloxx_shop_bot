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
        response = self.session.get(f"{self.base_url}/me", timeout=API_TIMEOUT)
        return response.json()
    
    def get_username(self):
        data = self.get_me()
        return data.get('user', {}).get('username', 'unknown')
    
    def get_balance(self):
        data = self.get_me()
        return data.get('user', {}).get('balance', '0')
    
    def get_balance_value(self):
        data = self.get_me()
        return data.get('user', {}).get('convertedBalance', 0)
    
    def get_items(self, **params):
        response = self.session.get(f"{self.base_url}/items", params=params, timeout=API_TIMEOUT)
        return response.json()
    
    def buy_item(self, item_id: int):
        response = self.session.post(f"{self.base_url}/items/{item_id}/buy", timeout=API_TIMEOUT)
        return response.json()