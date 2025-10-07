# # # bot/utils/ai_fallback.py
# # import os
# # import httpx
# # import json
# # from dotenv import load_dotenv

# # load_dotenv()

# # OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# # if not OPENROUTER_API_KEY:
# #     raise ValueError("❌ OPENROUTER_API_KEY не найден в .env")

# # async def ask_ai(user_query: str, context: str = "") -> str:
# #     system_prompt = (
# #         "Вы — эксперт по технической документации оборудования умного дома (HDL, Buspro, Matech, URRI и др.). "
# #         "Ваша задача — помочь пользователю найти нужную документацию или дать краткий, точный ответ. "
# #         "Если запрос неясен — задайте уточняющий вопрос. "
# #         "Если запрос не по теме — вежливо откажитесь."
# #     )
# #     if context:
# #         system_prompt += f" Доступные бренды: {context}."

# #     try:
# #         async with httpx.AsyncClient(timeout=30.0) as client:
# #             response = await client.post(
# #                 url="https://openrouter.ai/api/v1/chat/completions",
# #                 headers={
# #                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
# #                     "Content-Type": "application/json",
# #                     "HTTP-Referer": "https://t.me/HDL_Assistant_Bot",
# #                     "X-Title": "HDL Assistant Bot"
# #                 },
# #                 json={
# #                     "model": "deepseek/deepseek-chat-v3.1:free",
# #                     "messages": [
# #                         {"role": "system", "content": system_prompt},
# #                         {"role": "user", "content": user_query}
# #                     ],
# #                     "temperature": 0.3,
# #                     "max_tokens": 400
# #                 }
# #             )

# #             if response.status_code != 200:
# #                 print(f"OpenRouter error {response.status_code}: {response.text}")
# #                 return (
# #                     "ИИ временно недоступен. Попробуйте уточнить запрос:\n"
# #                     "• Укажите бренд (HDL, Buspro, Matech)\n"
# #                     "• Тип устройства (панель, контроллер, датчик)\n"
# #                     "• Модель (например, Granit, MDL64)"
# #                 )

# #             data = response.json()
# #             return data["choices"][0]["message"]["content"].strip()

# #     except Exception as e:
# #         print(f"Exception in AI call: {e}")
# #         return (
# #             "ИИ временно недоступен. Попробуйте уточнить запрос:\n"
# #             "• Укажите бренд (HDL, Buspro, Matech)\n"
# #             "• Тип устройства (панель, контроллер, датчик)\n"
# #             "• Модель (например, Granit, MDL64)"
# #         )

# # async def analyze_relevance(user_query: str, filename: str) -> bool:
# #     """
# #     Анализирует релевантность файла запросу пользователя через ИИ
# #     Возвращает True если файл релевантен, False если нет
# #     """
# #     prompt = f"""
# #     Анализ релевантности документа запросу пользователя.

# #     ЗАПРОС ПОЛЬЗОВАТЕЛЯ: "{user_query}"
# #     ИМЯ ФАЙЛА: "{filename}"

# #     Критерии анализа:
# #     1. "Интеграция Алисы с KNX" - это про подключение голосового помощника Яндекс Алиса к системе автоматизации KNX
# #     2. Технические паспорта датчиков (R5-60G-KNX, R5-24G-KNX) НЕ релевантны, если не указано про интеграцию с Алисой
# #     3. Релевантные файлы: руководства по интеграции, API, подключению, голосовому управлению
# #     4. Нерелевантные файлы: технические спецификации, паспорта оборудования, инструкции по монтажу

# #     Ответь ТОЛЬКО JSON формата:
# #     {{"relevant": true/false, "reason": "одно краткое предложение"}}

# #     Пример для НЕрелевантного:
# #     {{"relevant": false, "reason": "технический паспорт датчика не содержит информации об интеграции с Алисой"}}

# #     Пример для релевантного:
# #     {{"relevant": true, "reason": "файл содержит руководство по интеграции голосового управления"}}
# #     """

# #     try:
# #         async with httpx.AsyncClient(timeout=15.0) as client:
# #             response = await client.post(
# #                 url="https://openrouter.ai/api/v1/chat/completions",
# #                 headers={
# #                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
# #                     "Content-Type": "application/json",
# #                     "HTTP-Referer": "https://t.me/HDL_Assistant_Bot",
# #                     "X-Title": "HDL Assistant Bot"
# #                 },
# #                 json={
# #                     "model": "deepseek/deepseek-chat-v3.1:free",
# #                     "messages": [
# #                         {"role": "user", "content": prompt}
# #                     ],
# #                     "temperature": 0.1,
# #                     "max_tokens": 200
# #                 }
# #             )

# #             if response.status_code == 200:
# #                 data = response.json()
# #                 content = data["choices"][0]["message"]["content"].strip()
                
# #                 # Парсим JSON ответ
# #                 try:
# #                     result = json.loads(content)
# #                     return result.get("relevant", True)  # По умолчанию True если ошибка
# #                 except json.JSONDecodeError:
# #                     # Если ИИ вернул не JSON, анализируем текстовый ответ
# #                     if "не релевант" in content.lower() or "false" in content.lower():
# #                         return False
# #                     return True
# #             else:
# #                 print(f"OpenRouter error in relevance analysis: {response.status_code}")
# #                 return True  # По умолчанию показываем файл при ошибке
                
# #     except Exception as e:
# #         print(f"Exception in relevance analysis: {e}")
# #         return True  # По умолчанию показываем файл при ошибке





# # bot/utils/ai_fallback.py QWEEN
# import os
# import httpx
# import json
# import logging
# from dotenv import load_dotenv

# load_dotenv()

# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# if not OPENROUTER_API_KEY:
#     raise ValueError("❌ OPENROUTER_API_KEY не найден в .env")

# # Настройка логгера
# logger = logging.getLogger(__name__)

# async def ask_ai(user_query: str, context: str = "") -> str:
#     system_prompt = (
#         "Вы — эксперт по технической документации оборудования умного дома (HDL, Buspro, Matech, URRI и др.). "
#         "Ваша задача — помочь пользователю найти нужную документацию или дать краткий, точный ответ. "
#         "Если запрос неясен — задайте уточняющий вопрос. "
#         "Если запрос не по теме — вежливо откажитесь."
#     )
#     if context:
#         system_prompt += f" Доступные бренды: {context}."

#     try:
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 url="https://openrouter.ai/api/v1/chat/completions",  # ← без пробелов!
#                 headers={
#                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                     "Content-Type": "application/json",
#                     "HTTP-Referer": "https://t.me/HDL_Assistant_Bot",  # ← без пробелов!
#                     "X-Title": "HDL Assistant Bot"
#                 },
#                 json={
#                     "model": "google/gemma-2-9b-it:free",  # ← стабильная free-модель
#                     "messages": [
#                         {"role": "system", "content": system_prompt},
#                         {"role": "user", "content": user_query}
#                     ],
#                     "temperature": 0.3,
#                     "max_tokens": 400
#                 }
#             )

#             # 🔍 Логируем лимиты OpenRouter
#             limit = response.headers.get("X-RateLimit-Limit")
#             remaining = response.headers.get("X-RateLimit-Remaining")
#             if limit and remaining:
#                 logger.info(f"OpenRouter лимиты: {remaining}/{limit} запросов осталось")

#             if response.status_code == 429:
#                 logger.warning("OpenRouter: 429 Too Many Requests — лимит исчерпан")
#                 return (
#                     "⚠️ ИИ временно недоступен из-за высокой нагрузки. "
#                     "Попробуйте через 1–2 минуты или уточните запрос."
#                 )
#             elif response.status_code != 200:
#                 logger.error(f"OpenRouter error {response.status_code}: {response.text}")
#                 return (
#                     "ИИ временно недоступен. Попробуйте уточнить запрос:\n"
#                     "• Укажите бренд (HDL, Buspro, Matech)\n"
#                     "• Тип устройства (панель, контроллер, датчик)\n"
#                     "• Модель (например, Granit, MDL64)"
#                 )

#             data = response.json()
#             return data["choices"][0]["message"]["content"].strip()

#     except Exception as e:
#         logger.exception(f"Ошибка в ask_ai: {e}")
#         return (
#             "ИИ временно недоступен. Попробуйте позже или уточните запрос."
#         )


# # Опционально: функция анализа релевантности (если используется)
# async def analyze_relevance(user_query: str, filename: str) -> bool:
#     prompt = f"""
#     Анализ релевантности документа запросу пользователя.

#     ЗАПРОС: "{user_query}"
#     ФАЙЛ: "{filename}"

#     Ответь ТОЛЬКО JSON: {{"relevant": true/false, "reason": "..."}}
#     """

#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             response = await client.post(
#                 url="https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                     "Content-Type": "application/json",
#                     "HTTP-Referer": "https://t.me/HDL_Assistant_Bot",
#                     "X-Title": "HDL Assistant Bot"
#                 },
#                 json={
#                     "model": "google/gemma-2-9b-it:free",
#                     "messages": [{"role": "user", "content": prompt}],
#                     "temperature": 0.1,
#                     "max_tokens": 200
#                 }
#             )

#             # Логируем лимиты и для этого вызова
#             limit = response.headers.get("X-RateLimit-Limit")
#             remaining = response.headers.get("X-RateLimit-Remaining")
#             if limit and remaining:
#                 logger.info(f"[Relevance] Лимиты: {remaining}/{limit}")

#             if response.status_code == 200:
#                 content = response.json()["choices"][0]["message"]["content"].strip()
#                 try:
#                     result = json.loads(content)
#                     return result.get("relevant", True)
#                 except json.JSONDecodeError:
#                     return "не релевант" not in content.lower()
#             else:
#                 return True  # по умолчанию показываем

#     except Exception as e:
#         logger.exception(f"Ошибка в analyze_relevance: {e}")
#         return True

# bot/utils/ai_fallback.py
import os
import httpx
import json
import logging
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY не найден в .env")

logger = logging.getLogger(__name__)

# Счетчики для отслеживания использования
request_count = 0
token_count = 0

def log_rate_limits(response):
    """Логирует информацию о лимитах"""
    global request_count, token_count
    
    headers = response.headers
    limit = headers.get("X-RateLimit-Limit")
    remaining = headers.get("X-RateLimit-Remaining")
    reset = headers.get("X-RateLimit-Reset")
    
    # Лимиты по токенам
    token_limit = headers.get("X-RateLimit-Limit-Tokens")
    token_remaining = headers.get("X-RateLimit-Remaining-Tokens")
    
    request_count += 1
    
    logger.info("📊 OpenRouter Limits:")
    
    if limit and remaining:
        logger.info(f"   Запросы: {remaining}/{limit} (сброс через {reset}s)")
    
    if token_limit and token_remaining:
        # Преобразуем в тысячи для удобства чтения
        token_remaining_k = int(token_remaining) // 1000 if token_remaining else 0
        token_limit_k = int(token_limit) // 1000 if token_limit else 0
        logger.info(f"   Токены: ~{token_remaining_k}K/{token_limit_k}K")
    
    # Ваша статистика
    logger.info(f"   Ваша статистика: {request_count} запросов сегодня")

async def ask_ai(user_query: str, context: str = "") -> str:
    """
    Оптимизированная функция запросов к ИИ
    """
    # Проверяем длину запроса чтобы не тратить лишние токены
    if len(user_query) > 500:
        user_query = user_query[:500] + "..."
    
    system_prompt = (
        "Вы — эксперт по технической документации оборудования умного дома (HDL, Buspro, Matech, URRI). "
        "Отвечайте кратко и по делу. Если не знаете ответ — предложите связаться со специалистом."
    )
    if context:
        system_prompt += f" Бренды: {context}"

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://t.me/HDL_Assistant_Bot",
                    "X-Title": "HDL Assistant Bot"
                },
                json={
                    "model": "deepseek/deepseek-chat-v3.1:free",  # Стабильная бесплатная модель
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 350,  # Уменьшил с 400 для экономии
                    "top_p": 0.9
                }
            )

            # Логируем лимиты
            log_rate_limits(response)

            if response.status_code == 429:
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset = response.headers.get("X-RateLimit-Reset")
                
                if remaining == "0":
                    logger.warning("⏰ Лимиты исчерпаны! Ждем сброса...")
                    if reset:
                        minutes = int(reset) // 60
                        return (
                            f"⚠️ Бесплатные лимиты ИИ исчерпаны.\n\n"
                            f"Лимиты обновятся через ~{minutes} минут.\n\n"
                            f"А пока я могу:\n"
                            f"• 🔍 Найти документацию\n"
                            f"• 📚 Показать базу знаний\n"
                            f"• 📞 Связать со специалистом"
                        )
                
                return "ИИ временно недоступен. Попробуйте через несколько минут."
                
            elif response.status_code != 200:
                logger.error(f"Ошибка {response.status_code}: {response.text}")
                return get_fallback_response()

            data = response.json()
            
            # Логируем использование токенов
            usage = data.get('usage', {})
            if usage:
                total_tokens = usage.get('total_tokens', 0)
                logger.info(f"📝 Использовано токенов: {total_tokens}")
            
            answer = data["choices"][0]["message"]["content"].strip()
            
            # Проверяем качество ответа
            if len(answer) < 10 or "как ии" in answer.lower():
                return get_fallback_response()
                
            return answer

    except httpx.TimeoutException:
        logger.error("Таймаут запроса к ИИ")
        return "ИИ временно недоступен. Попробуйте позже."
        
    except Exception as e:
        logger.exception(f"Ошибка: {e}")
        return get_fallback_response()

def get_fallback_response() -> str:
    """Возвращает запасной ответ"""
    return (
        "🤖 ИИ временно недоступен.\n\n"
        "Что я могу сделать:\n"
        "• 🔍 Найти документацию по вашему запросу\n"
        "• 📚 Показать базу технической документации\n"
        "• 📞 Связать с техническим специалистом\n\n"
        "Попробуйте уточнить запрос или используйте кнопки ниже."
    )

# Упрощенная версия анализа релевантности для экономии токенов
async def analyze_relevance(user_query: str, filename: str) -> bool:
    """
    Упрощенный анализ релевантности без запросов к ИИ
    """
    query_lower = user_query.lower()
    filename_lower = filename.lower()
    
    # Для простых запросов по брендам - все файлы релевантны
    simple_brands = ["урри", "urri", "hdl", "баспро", "buspro", "матек", "matech"]
    if any(brand in query_lower for brand in simple_brands):
        return True
    
    # Для сложных запросов про интеграцию Алисы - фильтруем
    if "алис" in query_lower and "knx" in query_lower:
        # Исключаем технические паспорта
        exclude_patterns = ["r5-", "датчик", "sensor", "техническ", "паспорт"]
        if any(pattern in filename_lower for pattern in exclude_patterns):
            return False
        
        # Включаем файлы про интеграцию
        include_patterns = ["интеграци", "integration", "подключени", "connect", "руководств"]
        if any(pattern in filename_lower for pattern in include_patterns):
            return True
    
    return True