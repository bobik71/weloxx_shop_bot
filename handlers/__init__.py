# handlers/__init__.py
from aiogram import Router
import os
import importlib
import pkgutil

# Главный роутер, который будем импортировать в main.py
router = Router()

# Автоматически подключаем все .py файлы в папке handlers
package_dir = os.path.dirname(__file__)
for _, module_name, _ in pkgutil.iter_modules([package_dir]):
    if module_name == "__init__":
        continue
    try:
        module = importlib.import_module(f".{module_name}", package=__name__)
        # Подключаем, если в файле есть router или dp
        if hasattr(module, "router"):
            router.include_router(module.router)
        elif hasattr(module, "dp"):
            router.include_router(module.dp)
    except Exception as e:
        print(f"⚠️ Не удалось загрузить handler '{module_name}': {e}")