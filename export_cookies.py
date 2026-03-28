# export_cookies.py (альтернативная версия)
import sqlite3
import shutil
import os
import json
from pathlib import Path

# 🔹 Пути к базе куки (Windows)
CHROME_COOKIE_PATH = Path(os.environ['LOCALAPPDATA']) / "Google/Chrome/User Data/Default/Cookies"
EDGE_COOKIE_PATH = Path(os.environ['LOCALAPPDATA']) / "Microsoft/Edge/User Data/Default/Cookies"

def export_cookies(browser_path: Path, output_file: str = "lzt_cookies.json"):
    """Экспорт куки без прав админа (копируем файл)"""
    
    if not browser_path.exists():
        print(f"❌ Файл куки не найден: {browser_path}")
        return False
    
    # Копируем базу куки во временную папку
    temp_path = Path("temp_cookies.db")
    try:
        shutil.copy2(browser_path, temp_path)
    except PermissionError:
        print("❌ Нет доступа к файлу куки. Закройте браузер и попробуйте снова.")
        return False
    
    # Читаем куки из копии
    conn = sqlite3.connect(str(temp_path))
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name, value, host_key, path FROM cookies WHERE host_key LIKE '%lzt.market%'")
        rows = cursor.fetchall()
        
        if not rows:
            print("⚠️ Куки для lzt.market не найдены. Войдите на сайт в браузере.")
            return False
        
        cookie_list = []
        for row in rows:
            cookie_list.append({
                "name": row[0],
                "value": row[1],
                "domain": row[2],
                "path": row[3]
            })
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cookie_list, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Экспортировано {len(cookie_list)} куки в {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        conn.close()
        if temp_path.exists():
            temp_path.unlink()

# === ЗАПУСК ===
print("🔍 Экспорт куки lzt.market...\n")

# Пробуем Chrome
if export_cookies(CHROME_COOKIE_PATH):
    print("\n✅ Готово!")
else:
    print("\n🔹 Пробуем Edge...")
    if export_cookies(EDGE_COOKIE_PATH):
        print("\n✅ Готово!")
    else:
        print("\n❌ Не удалось экспортировать куки.")
        print("\n💡 Решение:")
        print("   1. Закройте браузер полностью")
        print("   2. Запустите скрипт снова")
        print("   3. Или используйте расширение (Способ 2)")