import os
import json
import logging
import re
import requests
import urllib.parse
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

# Конфигурация Яндекс.Диска
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

# Глобальные синонимы для поиска
SYNONYMS = {
    "кабель": "cable", "кникс": "knx", "кнх": "knx", "датчик": "sensor",
    "реле": "relay", "контроллер": "controller", "панель": "panel",
    "инструкция": "manual", "паспорт": "datasheet", "урри": "urri",
    "юрии": "urri", "хдл": "hdl", "баспро": "buspro", "баспр": "buspro",
    "матек": "matech", "матеч": "matech", "йилайт": "yeelight",
    "изикул": "easycool", "кабел": "cable", "замок": "lock",
    "дверной": "door", "иот": "iot", "айоти": "iot", "техничка": "technical"
}

def normalize_with_synonyms(query: str) -> str:
    """Нормализация текста с синонимами"""
    query_lower = query.lower().strip()
    for wrong, correct in sorted(SYNONYMS.items(), key=lambda x: -len(x[0])):
        query_lower = query_lower.replace(wrong, correct)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", query_lower)
    return re.sub(r"\s+", " ", cleaned).strip()

def get_folder_contents(path: str) -> List[Dict]:
    """Получение содержимого папки Яндекс.Диска"""
    url = f"{BASE_URL}/resources"
    params = {"path": path, "limit": 1000}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("_embedded", {}).get("items", [])

def build_docs_url(file_path: str) -> str:
    """Построение URL для просмотра документа"""
    base = YANDEX_DISK_FOLDER_PATH.rstrip("/")
    if file_path.startswith(base):
        relative_path = file_path[len(base):].lstrip("/")
    else:
        relative_path = file_path.lstrip("/")

    encoded_docs_key = urllib.parse.quote(DOCS_PUBLIC_KEY, safe="")
    encoded_path = urllib.parse.quote(relative_path, safe="/")
    filename = os.path.basename(file_path)
    encoded_name = urllib.parse.quote(filename, safe="")

    return (
        f"https://docs.360.yandex.ru/docs/view?"
        f"url=ya-disk-public%3A%2F%2F{encoded_docs_key}%3A%2F{encoded_path}"
        f"&name={encoded_name}&nosw=1"
    )

class SearchEngine:
    """Оптимизированный поисковый движок для документации"""

    def __init__(self, index_file: str = "data/cache/file_index.json"):
        self.index_file = index_file
        self.file_index = self.load_index()
        self._normalize_cache = {}

        self.synonyms = {
            "кабель": ["cable", "провод", "wire", "кабел"],
            "knx": ["кникс", "кнх", "knx"],
            "датчик": ["sensor", "сенсор", "детектор"],
            "реле": ["relay", "рел", "переключатель"],
            "контроллер": ["controller", "control", "управляющий"],
            "панель": ["panel", "панел"],
            "инструкция": ["manual", "instruction", "руководство"],
            "паспорт": ["datasheet", "technical", "технический"],
            "карниз": ["curtain", "track", "штора", "рельс"],
            "радиусный": ["изогнутый", "дуговой", "curved"],
            "спецификация": ["spec", "технические характеристики", "техничка"],
            "кондиционер": ["ac", "air conditioner", "климат", "сплит"],
            "совместимость": ["совместим", "работает с", "поддержка", "интеграция"],
            "модель": ["модели", "артикул", "серия"],
            "urri": ["урри", "юрии"],
            "hdl": ["хдл"],
            "buspro": ["баспро", "баспр"],
            "matech": ["матек", "матеч"],
            "yeelight": ["йилайт", "yee light"],
            "easycool": ["изикул", "easy cool", "изи кул"],
            "кабел": ["кабель", "cable"],
            "замок": ["lock", "дверной замок", "door lock"],
            "замки": ["locks", "дверные замки", "door locks"],
            "дверной": ["door", "дверной"],
            "iot": ["иот", "iot systems", "айоти"],
            "техничка": ["техническая", "technical", "документация", "паспорт"]
        }

        self.folder_links = {
            # Кабели
            "кабель": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "кабели": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "cable": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "техничка на кабель": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "кабель иот": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "кабель iot": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "iot кабель": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",

            # Замки
            "замок": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "замки": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "дверной замок": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "дверные замки": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "замки iot": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "замки иот": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "iot замок": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "door lock": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",

            # Алиса
            "алиса": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/02.%20HDL/09.%20%D0%98%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F%20%D1%81%20%D0%B3%D0%BE%D0%BB%D0%BE%D1%81%D0%BE%D0%B2%D1%8B%D0%BC%D0%B8%20%D0%B0%D1%81%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BD%D1%82%D0%B0%D0%BC%D0%B8.%20Buspro%20%D0%B8%20KNX",
            "яндекс алиса": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/02.%20HDL/09.%20%D0%98%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F%20%D1%81%20%D0%B3%D0%BE%D0%BB%D0%BE%D1%81%D0%BE%D0%B2%D1%8B%D0%BC%D0%B8%20%D0%B0%D1%81%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BD%D1%82%D0%B0%D0%BC%D0%B8.%20Buspro%20%D0%B8%20KNX",
            "голосовой ассистент": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/02.%20HDL/09.%20%D0%98%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F%20%D1%81%20%D0%B3%D0%BE%D0%BB%D0%BE%D1%81%D0%BE%D0%B2%D1%8B%D0%BC%D0%B8%20%D0%B0%D1%81%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BD%D1%82%D0%B0%D0%BC%D0%B8.%20Buspro%20%D0%B8%20KNX",
            "mgwip": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/02.%20HDL/09.%20%D0%98%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F%20%D1%81%20%D0%B3%D0%BE%D0%BB%D0%BE%D1%81%D0%BE%D0%B2%D1%8B%D0%BC%D0%B8%20%D0%B0%D1%81%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BD%D1%82%D0%B0%D0%BC%D0%B8.%20Buspro%20%D0%B8%20KNX",

            # Карнизы — точные совпадения
            "карниз buspro": "https://disk.360.yandex.ru/d/20Q51Ey5rDMXqA",
            "карниз баспро": "https://disk.360.yandex.ru/d/20Q51Ey5rDMXqA",
            "карниз бас про": "https://disk.360.yandex.ru/d/20Q51Ey5rDMXqA",
            "карнизы buspro": "https://disk.360.yandex.ru/d/20Q51Ey5rDMXqA",
            "карнизы баспро": "https://disk.360.yandex.ru/d/20Q51Ey5rDMXqA",
            "карниз knx": "https://disk.360.yandex.ru/d/x1w6XEUthCgTVg",
            "карниз кникс": "https://disk.360.yandex.ru/d/x1w6XEUthCgTVg",
            "карнизы knx": "https://disk.360.yandex.ru/d/x1w6XEUthCgTVg",
            "карнизы кникс": "https://disk.360.yandex.ru/d/x1w6XEUthCgTVg",
            "карниз по протоколу knx": "https://disk.360.yandex.ru/d/x1w6XEUthCgTVg",

            # Кондиционеры — точные совпадения
            "кондиционеры easycool": "https://disk.360.yandex.ru/d/EuWsEkI__LPmIQ",
            "easycool кондиционеры": "https://disk.360.yandex.ru/d/EuWsEkI__LPmIQ",
            "кондиционеры coolautomation": "https://disk.360.yandex.ru/d/UVzihaR7eRIRmw",
            "coolautomation кондиционеры": "https://disk.360.yandex.ru/d/UVzihaR7eRIRmw",

            # EasyCool
            "изикул": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "easycool": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "изи кул": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "техничка на изикул": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "документация изикул": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "паспорт на изикул": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "нужна техничка на изикул": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "изикул баспро": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "изикул knx": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
            "изикул buspro": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/03.%20iOT%20EasyCool",
        }

        # Ключевые слова
        self._alisa_keywords = {"алис", "яндекс алис", "yandex alice", "alisa", "mgwip", "голосов", "голосовой", "ассистент"}
        self._integration_keywords = {"интеграци", "настрои", "подключи", "связк", "связать", "объединить"}
        self._cable_keywords = {"кабель", "cable", "техничка на кабель", "кабель иот", "кабель iot", "iot кабель"}
        self._lock_keywords = {"замок", "замки", "дверной замок", "дверные замки", "замки iot", "замки иот", "iot замок"}
        self._easycool_keywords = {
            "изикул", "easycool", "изи кул", "техничка на изикул", "документация изикул",
            "паспорт на изикул", "нужна техничка на изикул", "изикул баспро", "изикул knx", "изикул buspro"
        }
        self._curtain_general_keywords = {
            "карниз", "карнизы", "радиусный карниз", "спецификация на карнизы",
            "паспорт карнизов", "техничка на карниз", "карниз по протоколу"
        }
        self._ac_general_keywords = {
            "кондиционер", "кондиционеры", "кондиционеры баспро", "кондиционеры совместимы",
            "кондиционеры модели", "совместимость кондиционеров", "кондиционеры с протоколом",
            "спецификация кондиционеров", "паспорт кондиционера", "техничка на кондиционер"
        }

    def load_index(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return list(data.values())
                    return data
            else:
                logging.warning(f"Index file {self.index_file} not found")
                return []
        except Exception as e:
            logging.error(f"Error loading index: {e}")
            return []

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        if text in self._normalize_cache:
            return self._normalize_cache[text]
        normalized = normalize_with_synonyms(text)
        self._normalize_cache[text] = normalized
        return normalized

    def expand_synonyms(self, query: str) -> List[str]:
        normalized_query = self.normalize_text(query)
        words = normalized_query.split()
        if not words:
            return [normalized_query]
        expanded_queries = {normalized_query}
        for i, word in enumerate(words):
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    new_words = words.copy()
                    new_words[i] = synonym
                    expanded_queries.add(' '.join(new_words))
        return list(expanded_queries)

    def should_redirect_to_folder(self, query: str) -> Tuple[bool, str]:
        query_lower = query.lower().strip()
        logging.info(f"🔍 Проверка перенаправления для: '{query}' -> '{query_lower}'")

        # Точное совпадение
        if query_lower in self.folder_links:
            logging.info(f"🎯 ТОЧНОЕ СОВПАДЕНИЕ: '{query}' -> папка")
            return True, self.folder_links[query_lower]

        # Кондиционеры
        if any(kw in query_lower for kw in self._ac_general_keywords):
            logging.info(f"🎯 ОБЩИЙ ЗАПРОС ПРО КОНДИЦИОНЕРЫ: '{query}' → обе папки")
            return True, "__AC_BOTH__"

        # Карнизы
        if any(kw in query_lower for kw in self._curtain_general_keywords):
            logging.info(f"🎯 ОБЩИЙ ЗАПРОС ПРО КАРНИЗЫ: '{query}' → обе папки")
            return True, "__CURTAINS_BOTH__"

        # EasyCool
        easycool_patterns = ["изикул", "easycool", "изи кул"]
        if any(pattern in query_lower for pattern in easycool_patterns):
            logging.info(f"🎯 EASYCOOL ЗАПРОС: '{query}' -> папка Easycool")
            return True, self.folder_links["изикул"]

        # Исключаем KNX из общих правил (обрабатывается отдельно)
        if "knx" in query_lower:
            return False, ""

        # Кабели и замки
        if any(kw in query_lower for kw in self._cable_keywords) and "knx" not in query_lower:
            return True, self.folder_links["кабель"]
        if any(kw in query_lower for kw in self._lock_keywords):
            return True, self.folder_links["замки"]

        logging.info(f"❌ Перенаправление не требуется для: '{query}'")
        return False, ""

    def is_knx_cable_query(self, query: str) -> bool:
        query_lower = query.lower().strip()
        exact_knx_queries = {
            "кабель knx", "knx кабель", "cable knx", "knx cable",
            "knx кабел", "ye00820", "j-y(st)y", "2x2x0,8"
        }
        if any(exact_query in query_lower for exact_query in exact_knx_queries):
            return True
        words = set(query_lower.split())
        has_knx = any("knx" in word for word in words)
        has_cable = any(word in {"кабель", "cable", "кабел"} for word in words)
        return has_knx and has_cable

    def is_alisa_integration_query(self, query: str) -> bool:
        query_lower = query.lower()
        has_alisa = any(keyword in query_lower for keyword in self._alisa_keywords)
        has_integration = any(keyword in query_lower for keyword in self._integration_keywords)
        return has_alisa and has_integration

    def get_alisa_integration_link(self) -> str:
        return self.folder_links["алиса"]

    def find_knx_cable_files(self) -> List[Dict[str, Any]]:
        knx_cable_keywords = [
            "ye00820", "j-y(st)y", "2x2x0,8", "knx кабель", "кабель knx", "кабель j-y", "j-y st y"
        ]
        scored_files = []
        for file_data in self.file_index:
            file_name = file_data.get("name", "").lower()
            file_path = file_data.get("path", "").lower()
            search_text = f"{file_name} {file_path}"
            score = 0
            for i, keyword in enumerate(knx_cable_keywords):
                if keyword in search_text:
                    score += (len(knx_cable_keywords) - i) * 100
            if score > 0:
                scored_files.append((score, file_data))
        scored_files.sort(key=lambda x: x[0], reverse=True)
        return [file_data for score, file_data in scored_files]

    def filter_irrelevant_results(self, results: List[Dict], query: str) -> List[Dict]:
        if not results:
            return []
        query_lower = query.lower()
        filtered_results = []
        for result in results:
            name = result.get('name', '').lower()
            if any(w in query_lower for w in ['интеграц', 'протокол', 'api', 'настройк', 'как']):
                if any(t in name for t in ['паспорт', 'datasheet', 'техническ', 'r5-', 'технический']):
                    continue
            if 'контроллер' in query_lower or 'controller' in query_lower:
                if any(irr in name for irr in ['датчик', 'sensor', 'реле', 'relay', 'кабель', 'cable']):
                    continue
            filtered_results.append(result)
        return filtered_results

    def calculate_relevance(self, file_data: Dict[str, Any], query_variants: List[str]) -> float:
        max_score = 0
        file_name = file_data.get("name", "").lower()
        file_path = file_data.get("path", "").lower()
        norm_name = file_data.get("norm_name", "").lower()
        search_text = f"{file_name} {file_path} {norm_name}"
        for query in query_variants:
            score = 0
            query_words = set(query.split())
            if query in file_name:
                score += 10
            if query_words.issubset(set(file_name.split())):
                score += 8
            if query in norm_name:
                score += 7
            if query in file_path:
                score += 6
            name_similarity = SequenceMatcher(None, query, file_name).ratio()
            path_similarity = SequenceMatcher(None, query, file_path).ratio()
            score += max(name_similarity, path_similarity) * 5
            for word in query_words:
                if word in file_name:
                    score += 2
                if word in norm_name:
                    score += 3
                if word in file_path:
                    score += 1
            if "кабель" in query and "knx" in query:
                knx_bonus = {
                    "ye00820": 100,
                    "j-y(st)y": 80,
                    "2x2x0,8": 60,
                    "knx кабель": 40,
                    "кабель knx": 40
                }
                for kw, bonus in knx_bonus.items():
                    if kw in search_text:
                        score += bonus
                if "датчик" in search_text:
                    score -= 50
            max_score = max(max_score, score)
        return max_score

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not query or not self.file_index:
            return []
        query_variants = self.expand_synonyms(query)
        scored_results = []
        for file_data in self.file_index:
            relevance = self.calculate_relevance(file_data, query_variants)
            if relevance > 0:
                scored_results.append({**file_data, "relevance": relevance})
        scored_results.sort(key=lambda x: x["relevance"], reverse=True)
        return scored_results[:limit]

    def hybrid_search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Алиса
        if self.is_alisa_integration_query(query):
            return [{
                "name": "📁 Документация по интеграции с Яндекс Алисой",
                "path": self.get_alisa_integration_link(),
                "is_folder_link": True,
                "folder_link": self.get_alisa_integration_link()
            }]

        # KNX кабель
        if self.is_knx_cable_query(query):
            knx_results = self.find_knx_cable_files()
            if knx_results:
                return knx_results[:limit]

        # Перенаправления
        should_redirect, folder_link = self.should_redirect_to_folder(query)
        if should_redirect:
            if folder_link == "__CURTAINS_BOTH__":
                return [
                    {"name": "Buspro", "path": "https://disk.360.yandex.ru/d/20Q51Ey5rDMXqA", "is_folder_link": True, "folder_link": "https://disk.360.yandex.ru/d/20Q51Ey5rDMXqA"},
                    {"name": "KNX", "path": "https://disk.360.yandex.ru/d/x1w6XEUthCgTVg", "is_folder_link": True, "folder_link": "https://disk.360.yandex.ru/d/x1w6XEUthCgTVg"}
                ]
            elif folder_link == "__AC_BOTH__":
                return [
                    {"name": "Для EasyCool", "path": "https://disk.360.yandex.ru/d/EuWsEkI__LPmIQ", "is_folder_link": True, "folder_link": "https://disk.360.yandex.ru/d/EuWsEkI__LPmIQ"},
                    {"name": "Для CoolAutomation", "path": "https://disk.360.yandex.ru/d/UVzihaR7eRIRmw", "is_folder_link": True, "folder_link": "https://disk.360.yandex.ru/d/UVzihaR7eRIRmw"}
                ]
            else:
                return [{
                    "name": f"📁 Папка с документацией: {query}",
                    "path": folder_link,
                    "is_folder_link": True,
                    "folder_link": folder_link
                }]

        # Обычный поиск
        improved_results = self.search(query, limit * 2)
        improved_results = self.filter_irrelevant_results(improved_results, query)
        if improved_results:
            return improved_results[:limit]

        # Fallback на старый поиск
        try:
            old_results = self.old_smart_search(query)
            return old_results[:limit]
        except Exception as e:
            logging.error(f"❌ Ошибка в старом поиске: {e}")
            return []

    def old_smart_search(self, query: str, limit: int = 3) -> List[Dict]:
        if not self.file_index:
            return []
        query_norm = self.normalize_text(query)
        if not query_norm:
            return []
        exact_results = self._old_search_exact_match(query_norm)
        if exact_results:
            return exact_results[:limit]
        combo_results = self._old_search_keyword_combinations(query_norm)
        if combo_results:
            return combo_results[:limit]
        important_results = self._old_search_important_keywords(query_norm)
        if important_results:
            return important_results[:limit]
        return []

    def _old_search_exact_match(self, query_norm: str) -> List[Dict]:
        keywords = [word for word in query_norm.split() if len(word) >= 2]
        if not keywords:
            return []
        results = []
        for file_data in self.file_index:
            norm_name = file_data.get("norm_name", "")
            if all(kw in norm_name for kw in keywords):
                results.append(file_data)
        return results

    def _old_search_keyword_combinations(self, query_norm: str) -> List[Dict]:
        keywords = [word for word in query_norm.split() if len(word) >= 2]
        if len(keywords) < 2:
            return []
        scored_files = []
        for file_data in self.file_index:
            norm_name = file_data.get("norm_name", "")
            file_name = file_data.get("name", "").lower()
            score = sum(20 for kw in keywords if kw in norm_name)
            score += sum(10 for kw in keywords if kw in file_name)
            if score > 0:
                scored_files.append((score, file_data))
        scored_files.sort(key=lambda x: x[0], reverse=True)
        return [fd for _, fd in scored_files]

    def _old_search_important_keywords(self, query_norm: str) -> List[Dict]:
        important_keywords = {"alisa", "knx", "integration", "connect", "gateway", "voice"}
        found = [kw for kw in important_keywords if kw in query_norm]
        if not found:
            return []
        scored = []
        for file_data in self.file_index:
            norm_name = file_data.get("norm_name", "")
            score = sum(30 for kw in found if kw in norm_name)
            if score > 0:
                scored.append((score, file_data))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [fd for _, fd in scored]


# Функции для обратной совместимости
async def smart_document_search(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    try:
        search_engine = SearchEngine()
        return search_engine.hybrid_search(query, limit)
    except Exception as e:
        logging.error(f"❌ Ошибка в smart_document_search: {e}")
        return []


def search_in_file_index(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
    search_engine = SearchEngine(index_path)
    return search_engine.search(query)


def has_only_technical_files(results: List[Dict[str, Any]]) -> bool:
    if results and results[0].get("is_folder_link"):
        return False
    technical_patterns = ["r5-", "датчик", "sensor", "техническ", "паспорт", "technical"]
    for file_data in results:
        name = file_data.get("name", "").lower()
        if not any(p in name for p in technical_patterns):
            return False
    return True


def should_use_ai_directly(query: str) -> bool:
    query_lower = query.lower()
    alisa_keywords = {
        "алис", "яндекс алис", "yandex alice", "alisa", "mgwip",
        "голосов", "голосовой", "ассистент", "шлюз", "интеграци"
    }
    if any(kw in query_lower for kw in alisa_keywords):
        return False
    complex_question_words = {
        "почему", "какой лучше", "что выбрать", "сравни", "отличия",
        "проблема", "ошибка", "не работает", "не подключается", "сломал"
    }
    is_complex = any(w in query_lower for w in complex_question_words)
    if is_complex and not any(kw in query_lower for kw in alisa_keywords):
        return True
    return False