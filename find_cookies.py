# find_cookies.py (с Firefox)
import os
from pathlib import Path

print("🔍 Поиск профилей Firefox...\n")

# Firefox хранит куки в другом месте
firefox_paths = [
    Path(os.environ['APPDATA']) / "Mozilla/Firefox/Profiles/",
]

for base_path in firefox_paths:
    if base_path.exists():
        print(f"✅ Папка профилей найдена: {base_path}")
        # Ищем папки профилей
        for profile in base_path.iterdir():
            if profile.is_dir():
                cookie_path = profile / "cookies.sqlite"
                if cookie_path.exists():
                    print(f"   ✅ Куки: {cookie_path}")
                else:
                    print(f"   ❌ Куки не найдены в: {profile.name}")
    else:
        print(f"❌ Firefox не найден: {base_path}")