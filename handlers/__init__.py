# handlers/__init__.py
from aiogram import Router
import os
import importlib
import logging

logger = logging.getLogger(__name__)

# Главный роутер
router = Router(name="weloxx_main")

# Автоматическое подключение всех .py файлов из папки handlers
current_dir = os.path.dirname(__file__)
for filename in os.listdir(current_dir):
    if filename.endswith(".py") and filename not in ("__init__.py",):
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f".{module_name}", package=__name__)
            
            if hasattr(module, "router"):
                router.include_router(module.router)
                logger.info(f"✅ Подключён роутер: {module_name}")
            else:
                # Не падаем, если в файле нет роутера (например, утилиты или вебхук обработчик)
                logger.warning(f"⚠️ В модуле '{module_name}' нет объекта 'router' — пропущен")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта '{module_name}': {type(e).__name__}: {e}")

__all__ = ["router"]