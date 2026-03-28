import os
import json
import shutil
import sqlite3
import base64
from pathlib import Path
from datetime import datetime

# --- Конфигурация ---
# Укажите домен, куки которого нужно забрать (например, для lz или магазина)
# Оставьте пустым "", чтобы выгрузить ВСЕ куки со всех сайтов
TARGET_DOMAIN = "" 
OUTPUT_FILE = "lzt_cookies.json"

# Пути к профилям браузеров (Windows)
BROWSERS = {
    'chrome': os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data'),
    'edge': os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data'),
    'brave': os.path.join(os.environ['LOCALAPPDATA'], 'BraveSoftware', 'Brave-Browser', 'User Data'),
    'opera': os.path.join(os.environ['APPDATA'], 'Opera Software', 'Opera Stable'),
    'firefox': os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles'),
    'yandex': os.path.join(os.environ['LOCALAPPDATA'], 'Yandex', 'YandexBrowser', 'User Data')
}

def get_master_key(browser_path):
    """Получает ключ расшифровки для Chrome/Edge (Local State)"""
    try:
        with open(os.path.join(browser_path, 'Local State'), 'r', encoding='utf-8') as f:
            key = json.loads(f.read())['os_crypt']['encrypted_key']
        # Удаляем префикс 'DPAPI'
        return win32crypt.CryptUnprotectData(base64.b64decode(key)[5:], None, None, None, 0)[1]
    except:
        return None

def decrypt_chrome_cookie(encrypted_value, master_key):
    """Расшифровывает куки Chrome/Edge"""
    try:
        if encrypted_value[:3] == b'v10' or encrypted_value[:3] == b'v11':
            # AES шифрование (новые версии)
            from Crypto.Cipher import AES
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:-16]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)
            return decrypted.decode('utf-8')
        else:
            # DPAPI (старые версии)
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8')
    except:
        return ""

def export_firefox(profile_path, output):
    """Экспорт из Firefox (без шифрования)"""
    src = os.path.join(profile_path, 'cookies.sqlite')
    if not os.path.exists(src):
        return False
    
    # Копируем, т.к. файл занят браузером
    temp_db = src + '.bak'
    try:
        shutil.copy2(src, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name, value, host FROM moz_cookies")
        
        cookies = {}
        for name, value, host in cursor.fetchall():
            if TARGET_DOMAIN and TARGET_DOMAIN not in host:
                continue
            cookies[name] = value
            
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=4)
            
        conn.close()
        os.remove(temp_db)
        return True
    except Exception as e:
        print(f"❌ Ошибка Firefox: {e}")
        return False

def export_chromium(browser_name, base_path, output):
    """Экспорт из Chrome/Edge/Opera"""
    # Ищем папку профиля (Default или Profile 1, 2...)
    profiles = []
    for item in os.listdir(base_path):
        if item.startswith('Profile') or item == 'Default':
            profiles.append(os.path.join(base_path, item))
    
    if not profiles:
        return False

    # Берем первый попавшийся профиль (обычно Default)
    profile_path = profiles[0]
    cookies_path = os.path.join(profile_path, 'Network', 'Cookies')
    
    if not os.path.exists(cookies_path):
        # Для старых версий или Opera
        cookies_path = os.path.join(profile_path, 'Cookies')

    if not os.path.exists(cookies_path):
        return False

    # Получаем ключ
    master_key = get_master_key(base_path)
    
    temp_db = cookies_path + '.bak'
    try:
        shutil.copy2(cookies_path, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name, encrypted_value, host_key FROM cookies")
        
        cookies = {}
        for name, encrypted_value, host in cursor.fetchall():
            if TARGET_DOMAIN and TARGET_DOMAIN not in host:
                continue
            
            value = ""
            if encrypted_value:
                if master_key:
                    value = decrypt_chrome_cookie(encrypted_value, master_key)
                else:
                    # Пробуем без ключа (редко работает на новых ОС)
                    try:
                        value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8')
                    except:
                        value = ""
            
            if value:
                cookies[name] = value
                
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=4)
            
        conn.close()
        os.remove(temp_db)
        return True
    except Exception as e:
        print(f"❌ Ошибка {browser_name}: {e}")
        return False

def main():
    print("🦊 Универсальный экспортер куки (All Browsers)")
    print("=" * 40)
    
    # Приоритет: Chrome -> Edge -> Firefox -> Opera
    found = False
    
    # 1. Пробуем Chromium браузеры
    for name, path in BROWSERS.items():
        if name == 'firefox':
            continue
        if os.path.exists(path):
            print(f"🔍 Найден браузер: {name.upper()}")
            if export_chromium(name, path, OUTPUT_FILE):
                print(f"✅ Успешно экспортировано из {name}")
                found = True
                break
    
    # 2. Если не нашли, пробуем Firefox
    if not found and os.path.exists(BROWSERS['firefox']):
        print(f"🔍 Найден браузер: FIREFOX")
        # Ищем первый профиль
        for item in os.listdir(BROWSERS['firefox']):
            if item.endswith('.default') or item.endswith('.default-release'):
                profile_path = os.path.join(BROWSERS['firefox'], item)
                if export_firefox(profile_path, OUTPUT_FILE):
                    print(f"✅ Успешно экспортировано из Firefox")
                    found = True
                    break
    
    if found:
        print("=" * 40)
        print(f"📁 Файл сохранён: {os.path.abspath(OUTPUT_FILE)}")
        
        # Проверка содержимого
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"📋 Найдено куки: {len(data)}")
            if len(data) > 0:
                print("✅ Файл валиден и готов к работе с ботом")
            else:
                print("⚠️ Файл пуст! Возможно, вы не авторизованы в браузере или неверно указан домен.")
        except:
            print("⚠️ Не удалось проверить файл")
    else:
        print("❌ Не найдено ни одного поддерживаемого браузера")
        print("💡 Убедитесь, что браузер установлен и вы вошли в аккаунт")

    input("\nНажмите Enter для выхода...")

# Для работы с шифрованием Chrome на Windows нужен win32crypt
# Если его нет, ставим: pip install pywin32
try:
    import win32crypt
except ImportError:
    print("⚠️ Отсутствует модуль win32crypt. Установка...")
    os.system("pip install pywin32")
    import win32crypt

if __name__ == '__main__':
    main()