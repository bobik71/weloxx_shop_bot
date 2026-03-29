# test_api.py
import json
from core.lzt_api import LZTClient

client = LZTClient()

try:
    response = client.get_me()
    
    # 🔍 Выводим ВСЁ, что пришло от API
    print("📄 Полный ответ API:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # 🔍 Проверяем структуру
    if 'user' in response:
        print("\n✅ Ключ 'user' найден!")
        print(f"📋 Доступные поля в user: {list(response['user'].keys())}")
    else:
        print("\n⚠️ Ключ 'user' не найден! Структура ответа другая.")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")