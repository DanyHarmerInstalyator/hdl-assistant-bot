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
import aiohttp
import json
import logging
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
logger = logging.getLogger(__name__)

async def ask_ai(user_query: str, context: str = "") -> str:
    """
    Функция запросов к ИИ через OpenRouter
    """
    if not OPENROUTER_API_KEY:
        return "ИИ временно недоступен. API ключ не настроен."
    
    # Проверяем длину запроса
    if len(user_query) > 500:
        user_query = user_query[:500] + "..."
    
    system_prompt = (
        "Вы — эксперт по технической документации оборудования умного дома (HDL, Buspro, Matech, URRI). "
        "Отвечайте кратко и по делу. Если не знаете ответ — предложите связаться со специалистом."
    )
    if context:
        system_prompt += f" Бренды: {context}"

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me/HDL_Assistant_Bot",
            "X-Title": "HDL Assistant Bot"
        }
        
        data = {
            "model": "google/gemma-2-9b-it:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.3,
            "max_tokens": 350,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                
                logger.info(f"📡 Статус ответа: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    answer = result['choices'][0]['message']['content'].strip()
                    logger.info("✅ ИИ ответил успешно")
                    return answer
                    
                elif response.status == 404:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка 404: {error_text}")
                    return (
                        "🤖 ИИ временно недоступен.\n\n"
                        "Для активации ИИ необходимо настроить политику приватности OpenRouter.\n\n"
                        "А пока я могу:\n"
                        "• 🔍 Найти документацию по вашему запросу\n"
                        "• 📚 Показать базу технической документации\n"
                        "• 📞 Связать с техническим специалистом"
                    )
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка {response.status}: {error_text}")
                    return get_fallback_response()

    except aiohttp.ClientError as e:
        logger.error(f"❌ Ошибка подключения: {e}")
        return "ИИ временно недоступен. Проблемы с подключением."
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
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

async def analyze_relevance(user_query: str, filename: str) -> bool:
    """
    Упрощенный анализ релевантности
    """
    query_lower = user_query.lower()
    filename_lower = filename.lower()
    
    simple_brands = ["урри", "urri", "hdl", "баспро", "buspro", "матек", "matech"]
    if any(brand in query_lower for brand in simple_brands):
        return True
    
    if "алис" in query_lower and "knx" in query_lower:
        exclude_patterns = ["r5-", "датчик", "sensor", "техническ", "паспорт"]
        if any(pattern in filename_lower for pattern in exclude_patterns):
            return False
        
        include_patterns = ["интеграци", "integration", "подключени", "connect", "руководств"]
        if any(pattern in filename_lower for pattern in include_patterns):
            return True
    
    return True