import os
import httpx
import json
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY не найден в .env")

logger = logging.getLogger(__name__)

class AIService:
    """Сервис для работы с ИИ через OpenRouter API"""
    
    def __init__(self):
        self.request_count = 0
        self.token_count = 0
        self.model = "google/gemma-2-9b-it:free"
        self.timeout = 25.0
        self.max_retries = 2

    def validate_query(self, user_query: str) -> tuple[bool, str]:
        """Проверяет валидность пользовательского запроса"""
        if not user_query or not user_query.strip():
            return False, "Пустой запрос"
        
        if len(user_query.strip()) < 3:
            return False, "Слишком короткий запрос"
        
        # Защита от потенциально опасных символов
        dangerous_patterns = ["../", "./", "/etc/", "/passwd"]
        if any(pattern in user_query for pattern in dangerous_patterns):
            return False, "Недопустимые символы в запросе"
        
        return True, "OK"

    def log_rate_limits(self, response: httpx.Response) -> None:
        """Логирует информацию о лимитах API"""
        try:
            headers = response.headers
            
            # Лимиты запросов
            limit = headers.get("X-RateLimit-Limit", "N/A")
            remaining = headers.get("X-RateLimit-Remaining", "N/A")
            reset = headers.get("X-RateLimit-Reset", "N/A")
            
            # Лимиты токенов
            token_limit = headers.get("X-RateLimit-Limit-Tokens", "N/A")
            token_remaining = headers.get("X-RateLimit-Remaining-Tokens", "N/A")
            
            self.request_count += 1
            
            logger.info("📊 OpenRouter Rate Limits:")
            logger.info(f"   Запросы: {remaining}/{limit} (reset: {reset}s)")
            
            if token_remaining != "N/A" and token_limit != "N/A":
                token_remaining_k = int(token_remaining) // 1000
                token_limit_k = int(token_limit) // 1000
                logger.info(f"   Токены: ~{token_remaining_k}K/{token_limit_k}K")
            
            logger.info(f"   Всего запросов: {self.request_count}")
            
        except Exception as e:
            logger.warning(f"Ошибка при логировании лимитов: {e}")

    def _prepare_system_prompt(self, context: str = "") -> str:
        """Подготавливает системный промпт с СТРОГИМ требованием русского языка"""
        system_prompt = (
            "ТЫ ДОЛЖЕН ОТВЕЧАТЬ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ! НИКАКОГО АНГЛИЙСКОГО!\n\n"
        "Ты — эксперт по технической документации оборудования умного дома.\n"
        "Поддерживаемые бренды: HDL, Buspro, Matech, URRI, iOT Systems, Yeelight Pro, CoolAutomation, Easycool.\n\n"
        "ЕСЛИ ПОЛЬЗОВАТЕЛЬ СПРАШИВАЕТ ПРО ЛЮБОЙ БРЕНД ИЛИ ПРОДУКТ:\n"
        "- Объясни что это за оборудование\n" 
        "- Предложи связаться со специалистом для подробной информации\n"
        "- НИКОГДА не говори что не понимаешь запрос\n\n"
        "Примеры правильных ответов на русском:\n"
        "'Easycool (Изикул) - это система климат-контроля от iOT Systems. "
        "Предлагаю связаться со специалистом для получения технической документации.'\n\n"
        "'URRI - это бренд аудио-видео оборудования для систем умного дома. "
        "Рекомендую обратиться к техническому специалисту для подбора решения.'\n\n"
        "ВАЖНО: Все ответы должны быть только на русском языке!\n"
        "Если не знаешь точного ответа - предложи связаться со специалистом.\n"
        "НЕ ГОВОРИ 'I don't understand' или 'It seems like'!\n\n"
        )
        if context:
            system_prompt += f"Контекст запроса: {context}\n\n"
        
        system_prompt += "Отвечай только на русском языке!"
        return system_prompt

    def _prepare_user_query(self, user_query: str) -> str:
        """Подготавливает пользовательский запрос"""
        # Обрезаем длинные запросы для экономии токенов
        if len(user_query) > 500:
            user_query = user_query[:497] + "..."
        return user_query

    def _handle_rate_limit(self, response: httpx.Response) -> str:
        """Обрабатывает превышение лимитов"""
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

    def _validate_ai_response(self, data: dict) -> tuple[bool, Optional[str]]:
        """Проверяет валидность ответа от ИИ"""
        try:
            # Проверяем структуру ответа
            if "choices" not in data or not data["choices"]:
                return False, "Некорректная структура ответа ИИ"
            
            choice = data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                return False, "Отсутствует содержимое ответа"
            
            answer = choice["message"]["content"].strip()
            
            # Проверяем качество ответа
            if len(answer) < 10:
                return False, "Слишком короткий ответ"
            answer = choice["message"]["content"].strip()

            
            return True, answer
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Ошибка валидации ответа ИИ: {e}")
            return False, None

    async def ask_ai(self, user_query: str, context: str = "") -> str:
        """
        Оптимизированная функция запросов к ИИ с retry логикой
        """
        # Валидация запроса
        is_valid, error_msg = self.validate_query(user_query)
        if not is_valid:
            return f"Некорректный запрос: {error_msg}"

        user_query = self._prepare_user_query(user_query)
        system_prompt = self._prepare_system_prompt(context)

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://t.me/HDL_Assistant_Bot",
                            "X-Title": "HDL Assistant Bot"
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_query}
                            ],
                            "temperature": 0.3,
                            "max_tokens": 350,
                            "top_p": 0.9
                        }
                    )

                    # Логируем лимиты
                    self.log_rate_limits(response)

                    # Обрабатываем ошибки API
                    if response.status_code == 429:
                        return self._handle_rate_limit(response)
                        
                    elif response.status_code != 200:
                        logger.error(f"Ошибка API {response.status_code}: {response.text}")
                        if attempt == self.max_retries - 1:
                            return get_fallback_response()
                        continue

                    data = response.json()
                    
                    # Логируем использование токенов
                    usage = data.get('usage', {})
                    if usage:
                        total_tokens = usage.get('total_tokens', 0)
                        logger.info(f"📝 Использовано токенов: {total_tokens}")
                    
                    # Валидируем и возвращаем ответ
                    is_valid, answer = self._validate_ai_response(data)
                    if is_valid and answer:
                        return answer
                    else:
                        logger.warning(f"Невалидный ответ ИИ: {answer}")
                        if attempt == self.max_retries - 1:
                            return get_fallback_response()

            except httpx.TimeoutException:
                logger.error(f"Таймаут запроса к ИИ (попытка {attempt + 1})")
                if attempt == self.max_retries - 1:
                    return "ИИ временно недоступен. Попробуйте позже."
                await asyncio.sleep(2 * (attempt + 1))  # экспоненциальная задержка
                
            except Exception as e:
                logger.exception(f"Ошибка при запросе к ИИ: {e}")
                if attempt == self.max_retries - 1:
                    return get_fallback_response()
                await asyncio.sleep(1)

        return get_fallback_response()

def get_fallback_response() -> str:
    """Возвращает запасной ответ"""
    return (
        "🤖 К сожалению, не удалось получить ответ от помощника.\n\n"
        "Что я могу сделать:\n"
        "• 🔍 Найти документацию по вашему запросу\n" 
        "• 📚 Показать базу технической документации\n"
        "• 📞 Связать с техническим специалистом\n\n"
        "Попробуйте уточнить запрос или используйте кнопки ниже."
    )

# Глобальный экземпляр для обратной совместимости
_ai_service = AIService()

async def ask_ai(user_query: str, context: str = "") -> str:
    """Функция для обратной совместимости"""
    return await _ai_service.ask_ai(user_query, context)

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