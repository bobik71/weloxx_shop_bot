
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Ваш НОВЫЙ ключ (после перевыпуска!)
API_KEY = os.getenv("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJzdWIiOjk4NzQ1NzQsImlzcyI6Imx6dCIsImlhdCI6MTc3NDYxODMzNiwianRpIjoiOTUyMjA3Iiwic2NvcGUiOiJiYXNpYyByZWFkIHBvc3QgY29udmVyc2F0ZSBwYXltZW50IGludm9pY2UgY2hhdGJveCBtYXJrZXQiLCJleHAiOjE5MzIyOTgzMzZ9.mACtGrDqS_r-TAF3oIvEzs4fIrhsC0LNHKfJYSNXsHVQUVmwDw5-Mqd6GTfZJWUPNnFh0zxlV3p5cKoGoSggEcDd8PeCwiWoqYkK1DgcGW-1QYxK3jpaRop5pukirk6w1zozB3mJn50Z2Qr61YZXXL_5_2TA4DomUmWZodrXVKE")

# Правильный базовый URL для форума
BASE_URL = "https://prod-api.lolz.live"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Тест: получение информации о текущем пользователе
response = requests.get(f"{BASE_URL}/user", headers=headers, timeout=10)

print(f"🔗 Запрос: {response.url}")
print(f"📡 Статус: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ Успех! Пользователь: {data.get('data', {}).get('username', 'N/A')}")
    print(f"🆔 ID: {data.get('data', {}).get('user_id', 'N/A')}")
elif response.status_code == 401:
    print("❌ Ошибка 401: Неверный или отозванный токен")
elif response.status_code == 403:
    print("❌ Ошибка 403: Нет прав (проверьте scope ключа)")
else:
    print(f"❌ Ошибка: {response.text[:200]}")