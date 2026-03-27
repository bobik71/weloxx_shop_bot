import re

def is_valid_price(value) -> bool:
    try: return float(value) > 0
    except: return False

def is_valid_category(cat: str) -> bool:
    return bool(re.match(r'^[a-z0-9_]{2,50}$', cat.lower()))

def sanitize(text: str, max_len: int = 500) -> str:
    return (text or "").strip()[:max_len]