import os
import json
import logging
import re
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

# Импортируем ваши существующие функции
from .yandex_disk_client import (
    normalize_with_synonyms, 
    smart_document_search as yandex_smart_search,
    build_docs_url
)

class SearchEngine:
    def __init__(self, index_file: str = "data/cache/file_index.json"):
        self.index_file = index_file
        self.file_index = self.load_index()
        self.synonyms = {
            "кабель": ["cable", "провод", "wire", "кабел"],
            "knx": ["кникс", "кнх", "knx"],
            "датчик": ["sensor", "сенсор", "детектор"],
            "реле": ["relay", "рел", "переключатель"],
            "контроллер": ["controller", "control", "управляющий"],
            "панель": ["panel", "панел"],
            "инструкция": ["manual", "instruction", "руководство"],
            "паспорт": ["datasheet", "technical", "технический"],
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

        # Специальные ссылки на папки Яндекс.Диска
        self.folder_links = {
            "кабель": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "кабели": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "cable": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "техничка на кабель": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "кабель иот": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "кабель iot": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            "iot кабель": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C",
            
            "замок": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "замки": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "дверной замок": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "дверные замки": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "замки iot": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "замки иот": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "iot замок": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems",
            "door lock": "https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems/04.%20%D0%94%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B7%D0%B0%D0%BC%D0%BA%D0%B8%20iOT%20Systems"
        }

    def load_index(self) -> List[Dict[str, Any]]:
        """Загрузка индекса из файла"""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Если это словарь, преобразуем в список
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
        """Нормализация текста для поиска"""
        if not text:
            return ""
        # Используем вашу существующую функцию нормализации
        return normalize_with_synonyms(text)

    def expand_synonyms(self, query: str) -> List[str]:
        """Расширяет запрос синонимами"""
        normalized_query = self.normalize_text(query)
        words = normalized_query.split()
        expanded_queries = [normalized_query]
        
        # Добавляем варианты с синонимами
        for i, word in enumerate(words):
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    new_words = words.copy()
                    new_words[i] = synonym
                    expanded_queries.append(' '.join(new_words))
        
        return list(set(expanded_queries))

    def should_redirect_to_folder(self, query: str) -> Tuple[bool, str]:
        """Проверяет, нужно ли перенаправить на папку Яндекс.Диска"""
        query_lower = query.lower().strip()
        
        # ИСКЛЮЧАЕМ запросы с KNX - они должны идти к специальному правилу
        if "knx" in query_lower:
            return False, ""
        
        # Проверяем точные совпадения
        if query_lower in self.folder_links:
            return True, self.folder_links[query_lower]
        
        # Проверяем частичные совпадения для кабелей (без KNX)
        cable_keywords = ["кабель", "cable", "техничка на кабель", "кабель иот", "кабель iot", "iot кабель"]
        if any(keyword in query_lower for keyword in cable_keywords) and "knx" not in query_lower:
            return True, self.folder_links["кабель"]
        
        # Проверяем частичные совпадения для замков
        lock_keywords = ["замок", "замки", "дверной замок", "дверные замки", "замки iot", "замки иот", "iot замок"]
        if any(keyword in query_lower for keyword in lock_keywords):
            return True, self.folder_links["замки"]
        
        return False, ""

    def is_knx_cable_query(self, query: str) -> bool:
        """Определяет, является ли запрос поиском кабеля KNX"""
        query_lower = query.lower().strip()
        
        # Конкретные запросы для кабеля KNX
        exact_knx_queries = [
            "кабель knx", "knx кабель", "cable knx", "knx cable",
            "knx кабел", "ye00820", "j-y(st)y", "2x2x0,8"
        ]
        
        # Проверяем точные совпадения
        if any(exact_query in query_lower for exact_query in exact_knx_queries):
            return True
        
        # Проверяем комбинации
        words = query_lower.split()
        has_knx = "knx" in words or any("knx" in word for word in words)
        has_cable = any(word in ["кабель", "cable", "кабел"] for word in words)
        
        return has_knx and has_cable

    def find_knx_cable_files(self) -> List[Dict[str, Any]]:
        """Принудительно ищет файлы кабеля KNX"""
        knx_cable_files = []
        
        for file_data in self.file_index:
            file_name = file_data.get("name", "").lower()
            file_path = file_data.get("path", "").lower()
            search_text = f"{file_name} {file_path}"
            
            # Ищем файлы кабеля KNX по ключевым признакам
            if any(keyword in search_text for keyword in [
                "ye00820", 
                "j-y(st)y", 
                "2x2x0,8",
                "knx кабель",
                "кабель knx",
                "кабель j-y",
                "j-y st y"
            ]):
                knx_cable_files.append(file_data)
        
        # Сортируем по релевантности
        scored_files = []
        for file_data in knx_cable_files:
            score = 0
            file_name = file_data.get("name", "").lower()
            file_path = file_data.get("path", "").lower()
            search_text = f"{file_name} {file_path}"
            
            # Высший приоритет для YE00820
            if "ye00820" in search_text:
                score += 1000
            if "j-y(st)y" in search_text:
                score += 500
            if "2x2x0,8" in search_text:
                score += 300
            if "knx кабель" in search_text or "кабель knx" in search_text:
                score += 200
                
            scored_files.append((score, file_data))
        
        scored_files.sort(key=lambda x: x[0], reverse=True)
        return [file_data for score, file_data in scored_files]

    def calculate_relevance(self, file_data: Dict[str, Any], query_variants: List[str]) -> float:
        """Вычисляет релевантность файла запросу"""
        max_score = 0
        
        file_name = file_data.get("name", "").lower()
        file_path = file_data.get("path", "").lower()
        norm_name = file_data.get("norm_name", "").lower()
        
        # Комбинируем все текстовые поля для поиска
        search_text = f"{file_name} {file_path} {norm_name}"
        
        for query in query_variants:
            score = 0
            
            # 1. Точное совпадение в названии (самый высокий приоритет)
            if query in file_name:
                score += 10
                
            # 2. Все слова запроса в названии
            query_words = set(query.split())
            file_name_words = set(file_name.split())
            if query_words.issubset(file_name_words):
                score += 8
                
            # 3. Точное совпадение в нормализованном имени
            if query in norm_name:
                score += 7
                
            # 4. Точное совпадение в пути
            if query in file_path:
                score += 6
                
            # 5. Частичное совпадение (похожесть строк)
            name_similarity = SequenceMatcher(None, query, file_name).ratio()
            path_similarity = SequenceMatcher(None, query, file_path).ratio()
            score += max(name_similarity, path_similarity) * 5
            
            # 6. Совпадение отдельных слов
            for word in query.split():
                if word in file_name:
                    score += 2
                if word in norm_name:
                    score += 3
                if word in file_path:
                    score += 1
            
            # 7. Специальные правила для кабелей KNX
            if "кабель" in query and "knx" in query:
                if "ye00820" in search_text:
                    score += 100
                if "j-y(st)y" in search_text:
                    score += 80
                if "2x2x0,8" in search_text:
                    score += 60
                if "knx кабель" in search_text or "кабель knx" in search_text:
                    score += 40
                if "датчик" in search_text:
                    score -= 50
            
            max_score = max(max_score, score)
        
        return max_score

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Улучшенный поиск документов по запросу"""
        if not query or not self.file_index:
            return []
        
        logging.info(f"🔍 Улучшенный поиск: '{query}'")
        
        # Расширяем запрос синонимами
        query_variants = self.expand_synonyms(query)
        logging.info(f"📋 Варианты запроса: {query_variants}")
        
        scored_results = []
        
        # Обрабатываем список файлов
        for file_data in self.file_index:
            relevance = self.calculate_relevance(file_data, query_variants)
            
            if relevance > 0:
                scored_results.append({
                    **file_data,
                    "relevance": relevance
                })
        
        # Сортируем по релевантности
        scored_results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Логируем топ-5 результатов для отладки
        for i, result in enumerate(scored_results[:5]):
            logging.info(f"🎯 Результат {i+1}: {result['name']} (релевантность: {result['relevance']:.2f})")
        
        return scored_results[:limit]

    def hybrid_search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Гибридный поиск: сначала проверяем специальные правила,
        затем обычный поиск
        """
        # 1. СПЕЦИАЛЬНОЕ ПРАВИЛО ДЛЯ КАБЕЛЯ KNX - САМЫЙ ВЫСШИЙ ПРИОРИТЕТ
        if self.is_knx_cable_query(query):
            knx_cable_results = self.find_knx_cable_files()
            if knx_cable_results:
                logging.info(f"🎯 КАБЕЛЬ KNX: найдено {len(knx_cable_results)} файлов")
                return knx_cable_results[:limit]

        # 2. ПРОВЕРКА ПЕРЕНАПРАВЛЕНИЯ НА ПАПКИ ЯНДЕКС.ДИСКА
        should_redirect, folder_link = self.should_redirect_to_folder(query)
        if should_redirect:
            logging.info(f"🎯 ПЕРЕНАПРАВЛЕНИЕ: запрос '{query}' → папка Яндекс.Диска")
            # Возвращаем специальный результат с ссылкой на папку
            return [{
                "name": f"📁 Папка с документацией: {query}",
                "path": folder_link,
                "is_folder_link": True,
                "folder_link": folder_link
            }]

        # 3. УЛУЧШЕННЫЙ ПОИСК
        improved_results = self.search(query, limit)
        if improved_results:
            logging.info(f"✅ Улучшенный поиск нашел {len(improved_results)} результатов")
            return improved_results
        
        # 4. СТАРЫЙ ПОИСК ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
        logging.info("🔄 Используем старый поисковый алгоритм")
        try:
            old_results = yandex_smart_search(query)
            return old_results[:limit]
        except Exception as e:
            logging.error(f"❌ Ошибка в старом поиске: {e}")
            return []


# Функции для обратной совместимости
async def smart_document_search(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Умный поиск документов (асинхронная версия)"""
    search_engine = SearchEngine()
    return search_engine.hybrid_search(query, limit)

def search_in_file_index(query: str, index_path: str = "data/cache/file_index.json") -> List[Dict]:
    """Старая функция поиска (для обратной совместимости)"""
    search_engine = SearchEngine(index_path)
    return search_engine.search(query)

def has_only_technical_files(results: List[Dict[str, Any]]) -> bool:
    """
    Проверяет, содержат ли результаты только технические файлы
    """
    # Если это ссылка на папку - не считаем техническим
    if results and results[0].get("is_folder_link"):
        return False
        
    technical_patterns = ["r5-", "датчик", "sensor", "техническ", "паспорт", "technical"]
    
    for file_data in results:
        file_name = file_data.get("name", "").lower()
        # Если есть хоть один НЕ технический файл - возвращаем False
        if not any(pattern in file_name for pattern in technical_patterns):
            return False
    
    # Все файлы технические
    return True

def should_use_ai_directly(query: str) -> bool:
    """
    Определяет, нужно ли сразу подключать ИИ без поиска документации
    """
    query_lower = query.lower()
    
    # Более широкий список ключевых слов для Алисы
    alisa_keywords = [
        "алис", "голосов", "яндекс алис", "yandex alice", "alisa", 
        "алису", "алисой", "алисы", "голосовой", "голосовое"
    ]
    
    # Более широкий список ключевых слов для интеграции
    integration_keywords = [
        "интеграци", "подключи", "настрои", "связать", "объединить", 
        "через", "с помощью", "вместе", "совместн", "как сделав", 
        "как настроив", "как подключив"
    ]
    
    has_alisa = any(keyword in query_lower for keyword in alisa_keywords)
    has_integration = any(keyword in query_lower for keyword in integration_keywords)
    has_knx = "knx" in query_lower or "кникс" in query_lower or "кнх" in query_lower
    
    # КРИТИЧЕСКИ ВАЖНО: Если есть Алиса И (интеграция ИЛИ KNX) - сразу к ИИ
    if has_alisa and (has_integration or has_knx):
        print("✅ Решение: Алиса + интеграция/KNX → сразу к ИИ")
        return True
    
    # Сложные вопросы про Алису
    question_words = ["как", "что", "какой", "какая", "можно ли", "возможно ли", "каков", "подскажи", "посоветуй"]
    if any(word in query_lower for word in question_words) and has_alisa:
        print("✅ Решение: вопрос про Алису → к ИИ")
        return True
    
    # Любой запрос содержащий "Алиса" и "KNX" вместе
    if has_alisa and has_knx:
        print("✅ Решение: Алиса + KNX → сразу к ИИ")
        return True
    
    print("❌ Решение: обычный поиск документации")
    return False