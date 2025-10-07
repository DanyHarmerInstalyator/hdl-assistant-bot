import json
import os
import time
from typing import Any, Dict

CACHE_DIR = "data/cache"
CACHE_FILE = os.path.join(CACHE_DIR, "relevance_cache.json")
CACHE_DURATION = 3600  # 1 час в секундах

def ensure_cache_dir():
    """Создает директорию для кэша если ее нет"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def load_cache() -> Dict[str, Any]:
    """Загружает кэш из файла"""
    ensure_cache_dir()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache: Dict[str, Any]):
    """Сохраняет кэш в файл"""
    ensure_cache_dir()
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except:
        pass

def get_cache_key(query: str, filename: str) -> str:
    """Генерирует ключ для кэша"""
    return f"{query.lower()}:{filename.lower()}"

def is_cache_valid(timestamp: float) -> bool:
    """Проверяет валидность кэша по времени"""
    return time.time() - timestamp < CACHE_DURATION