# import os
# import re
# import requests
# import urllib.parse
# import json
# from typing import List, Dict
# from dotenv import load_dotenv
# from .synonyms import SYNONYMS


# def normalize_with_synonyms(query: str) -> str:
#     query_lower = query.lower().strip()
#     for wrong, correct in sorted(SYNONYMS.items(), key=lambda x: -len(x[0])):
#         query_lower = query_lower.replace(wrong, correct)
#     cleaned = re.sub(r"[^a-z0-9\s]", " ", query_lower)
#     return re.sub(r"\s+", "", cleaned)

# load_dotenv()

# YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
# YANDEX_DISK_FOLDER_PATH = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
# DOCS_PUBLIC_KEY = os.getenv("DOCS_PUBLIC_KEY")

# if not YANDEX_DISK_TOKEN:
#     raise ValueError("❌ YANDEX_DISK_TOKEN не найден в .env")
# if not DOCS_PUBLIC_KEY:
#     raise ValueError("❌ DOCS_PUBLIC_KEY не найден в .env")


# BASE_URL = "https://cloud-api.yandex.net/v1/disk"

# HEADERS = {
#     "Authorization": f"OAuth {YANDEX_DISK_TOKEN}"
# }

# def normalize_text(s: str) -> str:
#     return re.sub(r"[^a-z0-9]", "", s.lower())

# def get_folder_contents(path: str) -> List[Dict]:
#     url = f"{BASE_URL}/resources"
#     params = {"path": path, "limit": 1000}
#     response = requests.get(url, headers=HEADERS, params=params)
#     response.raise_for_status()
#     data = response.json()
#     return data.get("_embedded", {}).get("items", [])

# def get_docs_public_key() -> str:
#     return DOCS_PUBLIC_KEY

# def build_docs_url(file_path: str) -> str:
#     docs_key = get_docs_public_key()
#     encoded_docs_key = urllib.parse.quote(docs_key, safe="")
#     base = YANDEX_DISK_FOLDER_PATH.rstrip("/")
#     if file_path.startswith(base):
#         relative_path = file_path[len(base):].lstrip("/")
#     else:
#         relative_path = file_path.lstrip("/")
#     encoded_path = urllib.parse.quote(relative_path, safe="/")
#     filename = os.path.basename(file_path)
#     encoded_name = urllib.parse.quote(filename, safe="")
#     return (
#         f"https://docs.360.yandex.ru/docs/view?"
#         f"url=ya-disk-public%3A%2F%2F{encoded_docs_key}%3A%2F{encoded_path}"
#         f"&name={encoded_name}&nosw=1"
#     )
# def search_in_file_index(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
#     if not os.path.exists(index_path):
#         return []
    
#     with open(index_path, "r", encoding="utf-8") as f:
#         files = json.load(f)
    
#     query_norm = normalize_with_synonyms(query)
#     if not query_norm:
#         return []

#     results = []
#     for f in files:
#         if query_norm in f["norm_name"] or f["norm_name"] in query_norm:
#             results.append(f)
#     return results


# bot/utils/yandex_disk_client.py QWEEN
# import os
# import re
# import requests
# import urllib.parse
# import json
# from typing import List, Dict
# from dotenv import load_dotenv
# from .synonyms import SYNONYMS
# from .ai_fallback import analyze_relevance

# def normalize_with_synonyms(query: str) -> str:
#     query_lower = query.lower().strip()
#     for wrong, correct in sorted(SYNONYMS.items(), key=lambda x: -len(x[0])):
#         query_lower = query_lower.replace(wrong, correct)
#     cleaned = re.sub(r"[^a-z0-9\s]", " ", query_lower)
#     return re.sub(r"\s+", " ", cleaned).strip()

# load_dotenv()

# YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
# YANDEX_DISK_FOLDER_PATH = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
# DOCS_PUBLIC_KEY = os.getenv("DOCS_PUBLIC_KEY")

# if not YANDEX_DISK_TOKEN:
#     raise ValueError("❌ YANDEX_DISK_TOKEN не найден в .env")
# if not DOCS_PUBLIC_KEY:
#     raise ValueError("❌ DOCS_PUBLIC_KEY не найден в .env")

# BASE_URL = "https://cloud-api.yandex.net/v1/disk"
# HEADERS = {
#     "Authorization": f"OAuth {YANDEX_DISK_TOKEN}"
# }

# def get_folder_contents(path: str) -> List[Dict]:
#     url = f"{BASE_URL}/resources"
#     params = {"path": path, "limit": 1000}
#     response = requests.get(url, headers=HEADERS, params=params)
#     response.raise_for_status()
#     data = response.json()
#     return data.get("_embedded", {}).get("items", [])

# def get_docs_public_key() -> str:
#     return DOCS_PUBLIC_KEY

# def build_docs_url(file_path: str) -> str:
#     docs_key = get_docs_public_key()
#     encoded_docs_key = urllib.parse.quote(docs_key, safe="")
#     base = YANDEX_DISK_FOLDER_PATH.rstrip("/")
#     if file_path.startswith(base):
#         relative_path = file_path[len(base):].lstrip("/")
#     else:
#         relative_path = file_path.lstrip("/")
#     encoded_path = urllib.parse.quote(relative_path, safe="/")
#     filename = os.path.basename(file_path)
#     encoded_name = urllib.parse.quote(filename, safe="")
#     return (
#         f"https://docs.360.yandex.ru/docs/view?"
#         f"url=ya-disk-public%3A%2F%2F{encoded_docs_key}%3A%2F{encoded_path}"
#         f"&name={encoded_name}&nosw=1"
#     )

# async def search_with_ai_relevance(query: str, index_path: str = "data/cache/file_index.json", limit: int = 3) -> List[Dict]:
#     """
#     Поиск с анализом релевантности через ИИ
#     """
#     if not os.path.exists(index_path):
#         return []
    
#     with open(index_path, "r", encoding="utf-8") as f:
#         files = json.load(f)
    
#     query_norm = normalize_with_synonyms(query)
#     print(f"🔍 Запрос: '{query}' -> Нормализованный: '{query_norm}'")
    
#     if not query_norm:
#         return []

#     # Сначала пробуем базовый поиск без ИИ
#     basic_results = basic_search(query_norm, files, limit=15)
    
#     if not basic_results:
#         return []
    
#     # Определяем нужен ли ИИ анализ
#     needs_ai_analysis = needs_ai_relevance_check(query, query_norm, basic_results)
    
#     if not needs_ai_analysis:
#         print(f"✅ ИИ анализ не требуется, возвращаем {len(basic_results)} результатов")
#         return basic_results[:limit]
    
#     # Используем ИИ анализ только для сложных случаев
#     print(f"🔍 Используем ИИ анализ для {len(basic_results)} кандидатов")
#     relevant_files = []
    
#     for file_data in basic_results[:8]:  # Ограничиваем количество для анализа
#         file_name = file_data.get("name", "")
#         is_relevant = await analyze_relevance(query, file_name)
#         if is_relevant:
#             relevant_files.append(file_data)
#         if len(relevant_files) >= limit:
#             break
    
#     print(f"✅ После ИИ анализа осталось {len(relevant_files)} релевантных файлов")
#     return relevant_files

# def needs_ai_relevance_check(original_query: str, normalized_query: str, results: List[Dict]) -> bool:
#     """
#     Определяет нужен ли анализ ИИ для данного запроса
#     """
#     # Простые запросы по брендам не требуют ИИ
#     simple_brands = ["urri", "hdl", "buspro", "matech", "yeelight", "dali", "granit"]
#     if normalized_query in simple_brands:
#         return False
    
#     # Запросы с одним словом обычно не требуют ИИ
#     if len(original_query.split()) <= 2:
#         return False
    
#     # Специфические запросы, которые требуют ИИ анализа
#     complex_keywords = ["интеграци", "подключи", "настрои", "алис", "голосов", "управлен"]
#     if any(keyword in original_query.lower() for keyword in complex_keywords):
#         return True
    
#     # Если в результатах есть файлы с "alisa" и "knx" - нужен ИИ для фильтрации
#     for file_data in results[:5]:
#         file_name = file_data.get("name", "").lower()
#         if "alisa" in file_name and "knx" in file_name:
#             return True
    
#     return False

# def basic_search(query_norm: str, files: List[Dict], limit: int = 15) -> List[Dict]:
#     """
#     Базовый поиск по ключевым словам без ИИ
#     """
#     scored_files = []
    
#     for file_data in files:
#         file_name = file_data.get("name", "").lower()
#         norm_name = file_data.get("norm_name", "")
        
#         score = 0
        
#         # Высокий приоритет: точное совпадение в нормализованном имени
#         if query_norm in norm_name:
#             score += 100
        
#         # Средний приоритет: совпадение в оригинальном имени
#         if query_norm in file_name:
#             score += 50
        
#         # Низкий приоритет: частичное совпадение
#         words = query_norm.split()
#         if words:
#             matched_words = sum(1 for word in words if word in norm_name)
#             score += matched_words * 10
        
#         if score > 0:
#             scored_files.append((score, file_data))
    
#     scored_files.sort(key=lambda x: x[0], reverse=True)
#     return [file_data for score, file_data in scored_files[:limit]]

# def smart_search(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
#     import asyncio
#     return asyncio.run(search_with_ai_relevance(query, index_path))

# def search_in_file_index(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
#     """
#     Ищет файлы, содержащие ВСЕ ключевые слова из запроса.
#     Пример: "Алиса KNX" → ищет файлы, где есть и "alisa", и "knx".
#     """
#     if not os.path.exists(index_path):
#         return []
    
#     with open(index_path, "r", encoding="utf-8") as f:
#         files = json.load(f)
    
#     query_norm = normalize_with_synonyms(query)
#     if not query_norm:
#         return []

#     # Разбиваем на ключевые слова (минимум 2 символа)
#     keywords = [word for word in re.split(r"[^a-z0-9]", query_norm) if len(word) >= 2]
    
#     if not keywords:
#         return []

#     results = []
#     for f in files:
#         norm_name = f["norm_name"]
#         # Требуем, чтобы ВСЕ ключевые слова присутствовали
#         if all(kw in norm_name for kw in keywords):
#             results.append(f)
    
#     return results

import os
import re
import requests
import urllib.parse
import json
from typing import List, Dict
from dotenv import load_dotenv
from .synonyms import SYNONYMS
from .ai_fallback import analyze_relevance

def normalize_with_synonyms(query: str) -> str:
    query_lower = query.lower().strip()
    for wrong, correct in sorted(SYNONYMS.items(), key=lambda x: -len(x[0])):
        query_lower = query_lower.replace(wrong, correct)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", query_lower)
    return re.sub(r"\s+", " ", cleaned).strip()

load_dotenv()

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
YANDEX_DISK_FOLDER_PATH = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
DOCS_PUBLIC_KEY = os.getenv("DOCS_PUBLIC_KEY")

if not YANDEX_DISK_TOKEN:
    raise ValueError("❌ YANDEX_DISK_TOKEN не найден в .env")
if not DOCS_PUBLIC_KEY:
    raise ValueError("❌ DOCS_PUBLIC_KEY не найден в .env")

BASE_URL = "https://cloud-api.yandex.net/v1/disk"
HEADERS = {
    "Authorization": f"OAuth {YANDEX_DISK_TOKEN}"
}

def get_folder_contents(path: str) -> List[Dict]:
    url = f"{BASE_URL}/resources"
    params = {"path": path, "limit": 1000}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("_embedded", {}).get("items", [])

def get_docs_public_key() -> str:
    return DOCS_PUBLIC_KEY

def build_docs_url(file_path: str) -> str:
    docs_key = get_docs_public_key()
    encoded_docs_key = urllib.parse.quote(docs_key, safe="")
    base = YANDEX_DISK_FOLDER_PATH.rstrip("/")
    if file_path.startswith(base):
        relative_path = file_path[len(base):].lstrip("/")
    else:
        relative_path = file_path.lstrip("/")
    encoded_path = urllib.parse.quote(relative_path, safe="/")
    filename = os.path.basename(file_path)
    encoded_name = urllib.parse.quote(filename, safe="")
    return (
        f"https://docs.360.yandex.ru/docs/view?"
        f"url=ya-disk-public%3A%2F%2F{encoded_docs_key}%3A%2F{encoded_path}"
        f"&name={encoded_name}&nosw=1"
    )

async def smart_document_search(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
    """
    Умный поиск документов с многоуровневой логикой
    """
    if not os.path.exists(index_path):
        return []
    
    with open(index_path, "r", encoding="utf-8") as f:
        files = json.load(f)
    
    query_norm = normalize_with_synonyms(query)
    print(f"🔍 Умный поиск: '{query}' -> Нормализованный: '{query_norm}'")
    
    if not query_norm:
        return []

    # Уровень 1: Точный поиск по всем ключевым словам
    exact_results = search_exact_match(query_norm, files)
    if exact_results:
        print(f"✅ Уровень 1: Найдено {len(exact_results)} точных совпадений")
        return exact_results[:3]

    # Уровень 2: Поиск по комбинациям ключевых слов
    combo_results = search_keyword_combinations(query_norm, files)
    if combo_results:
        print(f"✅ Уровень 2: Найдено {len(combo_results)} комбинаций")
        return combo_results[:3]

    # Уровень 3: Поиск по отдельным важным ключевым словам
    important_results = search_important_keywords(query_norm, files)
    if important_results:
        print(f"✅ Уровень 3: Найдено {len(important_results)} по важным словам")
        return important_results[:3]

    # Уровень 4: Анализ релевантности через ИИ (только для сложных запросов)
    if should_use_ai_analysis(query, query_norm):
        print(f"🔍 Уровень 4: Используем ИИ анализ")
        ai_results = await search_with_ai_relevance(query, files)
        if ai_results:
            print(f"✅ ИИ анализ: найдено {len(ai_results)} релевантных файлов")
            return ai_results[:3]

    return []

def search_exact_match(query_norm: str, files: List[Dict]) -> List[Dict]:
    """
    Поиск файлов, содержащих ВСЕ ключевые слова
    """
    keywords = [word for word in query_norm.split() if len(word) >= 2]
    if not keywords:
        return []

    results = []
    for file_data in files:
        norm_name = file_data.get("norm_name", "")
        if all(kw in norm_name for kw in keywords):
            results.append(file_data)
    
    return results

def search_keyword_combinations(query_norm: str, files: List[Dict]) -> List[Dict]:
    """
    Поиск по комбинациям ключевых слов (не обязательно всех)
    """
    keywords = [word for word in query_norm.split() if len(word) >= 2]
    if len(keywords) < 2:
        return []

    scored_files = []
    
    for file_data in files:
        norm_name = file_data.get("norm_name", "")
        file_name = file_data.get("name", "").lower()
        
        score = 0
        
        # Приоритетные комбинации для сложных запросов
        if "alisa" in norm_name and "knx" in norm_name:
            score += 100  # Высший приоритет для Алиса + KNX
        
        # Количество совпавших ключевых слов
        matched_keywords = sum(1 for kw in keywords if kw in norm_name)
        if matched_keywords >= 2:  # Хотя бы 2 ключевых слова
            score += matched_keywords * 20
        
        # Бонус за совпадение в оригинальном имени
        matched_in_original = sum(1 for kw in keywords if kw in file_name)
        score += matched_in_original * 10
        
        if score > 0:
            scored_files.append((score, file_data))
    
    scored_files.sort(key=lambda x: x[0], reverse=True)
    return [file_data for score, file_data in scored_files]

def search_important_keywords(query_norm: str, files: List[Dict]) -> List[Dict]:
    """
    Поиск по отдельным важным ключевым словам
    """
    important_keywords = ["alisa", "knx", "integration", "connect", "gateway", "voice"]
    
    # Находим важные ключевые слова в запросе
    found_important = [kw for kw in important_keywords if kw in query_norm]
    if not found_important:
        return []

    scored_files = []
    for file_data in files:
        norm_name = file_data.get("norm_name", "")
        
        score = 0
        for keyword in found_important:
            if keyword in norm_name:
                score += 30  # Высокий приоритет для важных слов
        
        if score > 0:
            scored_files.append((score, file_data))
    
    scored_files.sort(key=lambda x: x[0], reverse=True)
    return [file_data for score, file_data in scored_files]

def should_use_ai_analysis(original_query: str, normalized_query: str) -> bool:
    """
    Определяет, нужен ли анализ ИИ для данного запроса
    """
    # Сложные запросы, требующие понимания контекста
    complex_patterns = [
        "интеграци", "подключи", "настрои", "связать", "объединить",
        "алис", "голосов", "управлен", "как", "какой", "что нужно"
    ]
    
    query_lower = original_query.lower()
    
    # Запросы, которые явно требуют понимания контекста
    if any(pattern in query_lower for pattern in complex_patterns):
        return True
    
    # Запросы с несколькими концепциями (Алиса + KNX)
    if ("алис" in query_lower and "knx" in query_lower) or \
       ("голос" in query_lower and "knx" in query_lower):
        return True
    
    return False

async def search_with_ai_relevance(query: str, files: List[Dict]) -> List[Dict]:
    """
    Поиск с анализом релевантности через ИИ
    """
    # Берем топ-10 кандидатов для анализа
    candidate_files = files[:10]
    
    relevant_files = []
    for file_data in candidate_files:
        file_name = file_data.get("name", "")
        is_relevant = await analyze_relevance(query, file_name)
        if is_relevant:
            relevant_files.append(file_data)
        if len(relevant_files) >= 3:  # Ограничиваем результат
            break
    
    return relevant_files

# Старые функции для обратной совместимости
async def search_with_ai_relevance_old(query: str, index_path: str = "data/cache/file_index.json", limit: int = 3) -> List[Dict]:
    """Старая версия для обратной совместимости"""
    if not os.path.exists(index_path):
        return []
    
    with open(index_path, "r", encoding="utf-8") as f:
        files = json.load(f)
    
    return await search_with_ai_relevance(query, files)

def search_in_file_index(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
    """
    Старая функция поиска (для обратной совместимости)
    """
    if not os.path.exists(index_path):
        return []
    
    with open(index_path, "r", encoding="utf-8") as f:
        files = json.load(f)
    
    query_norm = normalize_with_synonyms(query)
    if not query_norm:
        return []

    return search_exact_match(query_norm, files)

def smart_search(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
    """Умный поиск (синхронная версия)"""
    import asyncio
    return asyncio.run(smart_document_search(query, index_path))