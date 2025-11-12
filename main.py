import os
import asyncio
import logging
import sys
import re
from typing import List, Dict
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

# Обновленные импорты после объединения файлов
from bot.utils.search_engine import smart_document_search, build_docs_url, should_use_ai_directly, has_only_technical_files
from bot.utils.ai_fallback import ask_ai
from keyboards import (
    main_reply_keyboard,
    docs_inline_keyboard,
    faq_main_inline,
    faq_software_inline,
    faq_hardware_inline,
    faq_partnership_inline,
    faq_knx_inline,
    faq_buspro_inline,
    faq_integrations_inline,
    faq_general_inline,
) 

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_DISK_FOLDER_PATH = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
YANDEX_DISK_PUBLIC_KEY = os.getenv("YANDEX_DISK_PUBLIC_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")  # URL от Render
PORT = int(os.getenv("PORT", 3000))

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

GREETINGS = {
    "привет", "здравствуйте", "добрый день", "доброе утро", "добрый вечер",
    "доброй ночи", "доброго дня", "приятного обеда", "приветствую", "хай", "hello", "hi"
}

SIMPLE_QUERIES = {"урри", "urri", "hdl", "баспро", "buspro", "матек", "matech", "йилайт", "yeelight"}

class SupportForm(StatesGroup):
    name = State()
    phone = State()
    original_query = State()

class DialogState(StatesGroup):
    waiting_for_clarification = State()

def should_use_ai_improved(query: str) -> bool:
    """
    Улучшенная логика определения когда использовать ИИ
    """
    query_lower = query.lower().strip()
    
    # ВЫСШИЙ ПРИОРИТЕТ: Запросы, которые НИКОГДА не идут к ИИ (документация и бренды)
    never_use_ai_keywords = {
        # Бренды и продукты
        "изикул", "easycool", "урри", "urri", "хдл", "hdl", "баспро", "buspro", 
        "матек", "matech", "йилайт", "yeelight", "изи кул", "карниз", "карнизы", "радиусный", "спецификация карнизов", "паспорт карнизов",
        
        # Документация
        "техничка", "документация", "паспорт", "инструкция", "руководство", "manual",
        "скачать", "файл", "pdf", "схема", "чертеж", "техническ",
        
        # Конкретные запросы документации
        "техничка на", "документация на", "паспорт на", "инструкция на"
    }
    
    # Если запрос содержит ключевые слова документации - НЕ использовать ИИ
    if any(keyword in query_lower for keyword in never_use_ai_keywords):
        logging.info(f"❌ Решение: запрос документации '{query}' → обычный поиск")
        return False
    
    # Запросы, которые сразу идут к ИИ (сложные технические вопросы)
    ai_direct_keywords = {
        # Общие технические вопросы
        "как интегрировать", "как подключить", "как настроить", "как работает",
        "как сделать", "как использовать", "как реализовать", "как объединить",
        
        # Сравнения и выбор
        "какой лучше", "что выбрать", "сравните", "отличия", "разница между",
        "преимущества", "недостатки", "плюсы и минусы",
        
        # Проблемы и ошибки
        "проблема с", "ошибка", "не работает", "не подключается", 
        "не настраивается", "сломал", "не отвечает",
        
        # Объяснения
        "почему", "зачем", "как устроен", "принцип работы", "объясните",
        "расскажите о", "что такое", "в чем разница",
        
        # Сложные технические темы
        "протокол", "интеграци", "api", "rest api", "websocket", "mqtt",
        "knx ip", "bacnet", "modbus", "zigbee", "z-wave", "wi-fi",
        "автоматизаци", "сценарий", "сценар", "логика"
    }
    
    # Проверяем, содержит ли запрос ключевые слова для прямого подключения к ИИ
    has_ai_keywords = any(keyword in query_lower for keyword in ai_direct_keywords)
    
    # Особые случаи для Алисы
    alisa_keywords = {
        "алис", "яндекс алис", "yandex alice", "alisa", "mgwip", 
        "голосов", "голосовой", "ассистент", "шлюз"
    }
    
    if any(keyword in query_lower for keyword in alisa_keywords):
        # Для Алисы с интеграцией - поиск, для сложных вопросов - ИИ
        if any(word in query_lower for word in ["интеграци", "настрои", "подключи"]):
            logging.info(f"❌ Решение: запрос про интеграцию Алисы '{query}' → обычный поиск")
            return False
        else:
            logging.info(f"✅ Решение: сложный вопрос про Алису '{query}' → к ИИ")
            return True
    
    # Логика принятия решения
    if has_ai_keywords:
        logging.info(f"✅ Решение: сложный технический запрос '{query}' → к ИИ")
        return True
    
    # Для коротких запросов - обычный поиск
    if len(query_lower.split()) <= 2:
        logging.info(f"❌ Решение: короткий запрос '{query}' → обычный поиск")
        return False
    
    # По умолчанию для сложных запросов используем ИИ
    words_count = len(query_lower.split())
    if words_count >= 4:  # Длинные запросы скорее всего сложные вопросы
        # Но проверяем, не является ли это запросом документации
        if any(doc_word in query_lower for doc_word in ["найди", "скинь", "дай", "сбрось", "отправь"]):
            logging.info(f"❌ Решение: запрос на поиск документации '{query}' → обычный поиск")
            return False
        logging.info(f"✅ Решение: длинный сложный запрос '{query}' → к ИИ")
        return True
    
    logging.info(f"❌ Решение: обычный запрос '{query}' → обычный поиск")
    return False

def extract_brands_from_query(query: str) -> str:
    """Извлекает бренды из запроса для контекста ИИ"""
    query_lower = query.lower()
    brands = []
    
    brand_keywords = {
        "hdl": "HDL",
        "урри": "URRI", 
        "urri": "URRI",
        "баспро": "Buspro",
        "buspro": "Buspro",
        "матек": "Matech",
        "matech": "Matech",
        "иот": "iOT Systems",
        "iot": "iOT Systems",
        "алис": "Яндекс Алиса",
        "alisa": "Яндекс Алиса",
        "yeelight": "Yeelight Pro",
        "йилайт": "Yeelight Pro",
        "coolautomation": "CoolAutomation",
        "dali": "Dali",
        "дали": "Dali",
        "easycool": "Easycool",
        "изикул": "Easycool"
    }
    
    for keyword, brand in brand_keywords.items():
        if keyword in query_lower:
            brands.append(brand)
    
    return ", ".join(set(brands)) if brands else ""

def format_search_results(results: List[Dict], query: str) -> str:
    """Форматирует результаты поиска в читаемый вид"""
    if not results:
        return "❌ По вашему запросу ничего не найдено"
    
    response = f"🔍 Результаты поиска по: '{query}'\n\n"
    
    for i, result in enumerate(results[:5], 1):
        name = result.get('name', 'Без названия')
        docs_url = build_docs_url(result['path']) if 'path' in result else result.get('folder_link', '#')
        
        if result.get('is_folder_link'):
            response += f"{i}. 📁 {name}\n   └─ 🔗 [Открыть папку]({docs_url})\n\n"
        else:
            response += f"{i}. {name}\n   └─ 📎 [Открыть документ]({docs_url})\n\n"
    
    response += "Полученная информация вам помогла?"
    return response

# --- Обработчики ---
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! 👨‍💻 Я HDL Assistant — помогу найти документацию или подключу к специалисту.\n\n"
        "🤔 Запутались в документации? 📑 Нужна спецификация или мануал? 🚀 Я с радостью помогу! ✨\n"
        "Используйте кнопки ниже или напишите запрос вручную:",
        reply_markup=main_reply_keyboard
    )

@dp.message(lambda msg: msg.text == "📚 База документации")
async def handle_docs_base(message: Message):
    await message.answer(
        "📂 База технической документации:\nhttps://disk.360.yandex.ru/d/xJi6eEXBTq01sw",
        reply_markup=docs_inline_keyboard
    )

@dp.message(lambda msg: msg.text == "🎓 Обучающие материалы")
async def handle_courses(message: Message):
    await message.answer("🎓 Обучающая платформа HDL:\nhttps://iotsystems.getcourse.ru/teach/control")
    
    

# ---START Обработчики FAQ ------------------------------------------------------------------------------------------------------------------------------------




# --- Обработчики FAQ ---
@dp.message(lambda msg: msg.text == "❓ FAQ: Часто Задаваемые Вопросы")
async def handle_faq_button(message: Message):
    await message.answer(
        "Выберите категорию вопросов:",
        reply_markup=faq_main_inline
    )

@dp.callback_query(lambda c: c.data == "faq_back_to_main")
async def faq_back_to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите категорию вопросов:",
        reply_markup=faq_main_inline
    )

# 1. Вопросы по ПО
@dp.callback_query(lambda c: c.data == "faq_software")
async def faq_software_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Вопросы по ПО:",
        reply_markup=faq_software_inline
    )

# 2. Вопросы по оборудованию
@dp.callback_query(lambda c: c.data == "faq_hardware")
async def faq_hardware_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Вопросы по оборудованию:",
        reply_markup=faq_hardware_inline
    )

# 3. Вопросы о сотрудничестве
@dp.callback_query(lambda c: c.data == "faq_partnership")
async def faq_partnership_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Вопросы о сотрудничестве:",
        reply_markup=faq_partnership_inline
    )

# 4. KNX
@dp.callback_query(lambda c: c.data == "faq_knx")
async def faq_knx_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "KNX:",
        reply_markup=faq_knx_inline
    )

# 5. BusPro
@dp.callback_query(lambda c: c.data == "faq_buspro")
async def faq_buspro_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "BusPro:",
        reply_markup=faq_buspro_inline
    )

# 6. Приложения/интеграции
@dp.callback_query(lambda c: c.data == "faq_integrations")
async def faq_integrations_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Приложения и интеграции:",
        reply_markup=faq_integrations_inline
    )

# 7. Общие вопросы
@dp.callback_query(lambda c: c.data == "faq_general")
async def faq_general_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Общие вопросы:",
        reply_markup=faq_general_inline
    )

# ---END Обработчики FAQ ------------------------------------------------------------------------------------------------------------------------------------



@dp.message(lambda msg: msg.text == "📞 Тех. специалист")
async def handle_support_button(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, укажите ваше ФИО:")
    await state.set_state(SupportForm.name)

@dp.message(SupportForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Укажите ваш номер телефона (10 цифр, без +7):\n\nПример: <code>9777809807</code>", parse_mode="HTML")
    await state.set_state(SupportForm.phone)

@dp.message(SupportForm.phone)
async def process_phone(message: Message, state: FSMContext):
    user_input = message.text.strip()
    digits_only = re.sub(r"\D", "", user_input)
    if len(digits_only) != 10:
        await message.answer("❌ Неверный формат. Введите ровно 10 цифр (без +7):\nПример: <code>9777809807</code>", parse_mode="HTML")
        return
    full_phone = f"+7{digits_only}"
    await state.update_data(phone=full_phone)
    data = await state.get_data()
    name = data["name"]
    original_query = data.get("original_query", "Запрос не указан")
    support_text = (
        f"📩 Новая заявка:\n\n"
        f"👤 ФИО: {name}\n"
        f"📱 Телефон: {full_phone}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"🔗 @ {message.from_user.username or '—'}\n\n"
        f"❓ Вопрос: {original_query}"
    )
    GROUP_CHAT_ID = -1003044266223
    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=support_text)
        await message.answer("✅ Заявка отправлена! Специалист скоро свяжется с вами.")
    except Exception as e:
        logging.error(f"Ошибка отправки в группу: {e}")
        await message.answer("Не удалось отправить заявку. Напишите напрямую: https://t.me/hdl_support")
    await state.clear()

async def handle_ai_with_context(message: Message, query: str, state: FSMContext):
    """Обработка ИИ с сохранением контекста"""
    thinking_msg = await message.answer("🤔 Анализирую ваш вопрос...")
    
    # Получаем текущее состояние
    data = await state.get_data()
    ai_response_count = data.get("ai_response_count", 0) + 1
    await state.update_data(
        original_query=query,
        ai_response_count=ai_response_count
    )
    
    # Извлекаем бренды и создаем улучшенный контекст
    brands_context = extract_brands_from_query(query)
    
    # Улучшенный системный промпт для технических вопросов
    context = (
        "ТЫ ДОЛЖЕН ОТВЕЧАТЬ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ! НИКАКОГО АНГЛИЙСКОГО!\n\n"
        "Ты — технический эксперт по оборудованию умного дома.\n"
        f"Бренды: {brands_context if brands_context else 'HDL, Buspro, Matech, URRI, iOT Systems, Yeelight Pro, CoolAutomation, Easycool, Dali'}.\n\n"
        "ВАЖНО: Если пользователь спрашивает о совместимости оборудования:\n"
        "1. Уточни какие конкретно устройства интересуют\n"
        "2. Объясни общие принципы совместимости\n"
        "3. Предложи связаться со специалистом для точного ответа\n"
        "4. Если известны конкретные модели - дай информацию по ним\n\n"
        "Отвечай подробно и технически грамотно, но если информации недостаточно - честно говори об этом.\n\n"
        "ПРИМЕР ХОРОШЕГО ОТВЕТА:\n"
        "'64-канальное реле может быть совместимо со шлюзом Dali при наличии соответствующего интерфейса. "
        "Для точного ответа необходимо знать конкретные модели реле и шлюза. "
        "Рекомендую обратиться к технической документации или специалисту.'"
    )
    
    ai_response = await ask_ai(query, context=context)
    
    # Формируем кнопки
    inline_buttons = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data="info_helpful:yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="info_helpful:no")
        ]
    ]
    
    # Добавляем кнопку "Тех. Специалист" при втором и последующих ответах от ИИ
    if ai_response_count >= 2:
        inline_buttons.append([
            InlineKeyboardButton(text="📞 Тех. Специалист", callback_data="support_form")
        ])
    
    await thinking_msg.edit_text(
        f"🧠 {ai_response}\n\nПолученная информация вам помогла?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    )
    
    await state.update_data(
        previous_response=ai_response,
        clarification_count=0
    )

async def handle_search_with_context(message: Message, query: str, state: FSMContext):
    """Обработка поиска с сохранением контекста"""
    search_message = await message.answer(f"🔍 Ищу документацию по: {query}")
    
    try:
        results = await smart_document_search(query)

        if results:
            # Проверяем, является ли результат ссылкой на папку
            if len(results) == 1 and results[0].get("is_folder_link"):
                folder_link = results[0].get("folder_link")
                await search_message.edit_text(
                    f"📁 <b>Документация по запросу: {query}</b>\n\n"
                    f"Для просмотра всей документации перейдите по ссылке:\n"
                    f"🔗 <a href='{folder_link}'>Открыть папку на Яндекс.Диске</a>\n\n"
                    f"В папке вы найдете все доступные документы, инструкции и технические паспорта.",
                    parse_mode="HTML"
                )
                return
            
            # Стандартный вывод результатов поиска
            response = f"🔍 Результаты поиска по: <b>{query}</b>\n\n"
            response += f"✅ Найдено документов: {len(results)}\n\n"
            
            for i, file_data in enumerate(results[:3], 1):
                try:
                    # СПЕЦИАЛЬНАЯ ССЫЛКА ДЛЯ КАБЕЛЯ KNX YE00820
                    if file_data.get("is_folder_link"):
                        direct_link = file_data["folder_link"]
                    else:
                        file_name = file_data.get("name", "").lower()
                        if "ye00820" in file_name and "knx" in file_name:    
                            direct_link = "https://docs.360.yandex.ru/docs/view?url=ya-disk-public%3A%2F%2Fh1up8PyRs7zLi0hvFuTbhsLh7Nh2dv1lmMR1wsc5WOjH0pYg8ba5c4cLlLY6oeuWtFP6gwbjvtaafTptcua4SA%3D%3D%3A%2F01.%20iOT%20Systems%2F02.%20iOT%20%D0%9A%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C%2FYE00820%20KNX%20%D0%BA%D0%B0%D0%B1%D0%B5%D0%BB%D1%8C%20J-Y(ST)Y%2C%202x2x0%2C8%2C%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D1%8B%D0%B9%20(%D0%BF%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%BB%D1%8F%D0%B5%D1%82%D1%81%D1%8F%20%D0%BF%D0%BE%20100%D0%BC)%2FYE00820%20ru.pdf&name=YE00820%20ru.pdf&nosw=1"
                        else:
                            direct_link = build_docs_url(file_data["path"])
                    
                    # Форматируем вывод с кликабельными ссылками
                    response += f"{i}. <b>{file_data['name']}</b>\n"
                    response += f"   └─ 📎 <a href='{direct_link}'>Открыть документ</a>\n\n"
                    
                except Exception as e:
                    logging.error(f"Ошибка генерации ссылки: {e}")
                    response += f"{i}. <b>{file_data['name']}</b>\n"
                    response += f"   └─ 📎 Файл в базе документации\n\n"
            
            response += "Полученная информация вам помогла?"
            
            await search_message.edit_text(
                response,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Да", callback_data="info_helpful:yes"),
                        InlineKeyboardButton(text="❌ Нет", callback_data="info_helpful:no")
                    ]
                ]),
                parse_mode="HTML"
            )
            
            # Если нашли только технические паспорта для сложного запроса
            if len(results) == 1 and has_only_technical_files(results):
                await message.answer(
                    "🤔 Кажется, это техническая документация, а не руководство по интеграции.\n\n"
                    "Могу подключить ИИ-помощника для более точного ответа:",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🧠 Спросить у ИИ", callback_data="ask_ai_current")]
                    ])
                )
            
        else:
            # Если документы не найдены - подключаем ИИ
            await search_message.edit_text("❌ Документация не найдена. Подключаю ИИ-помощника...")
            await handle_ai_with_context(message, query, state)
            
    except Exception as e:
        logging.error(f"Ошибка поиска: {e}")
        await search_message.edit_text(
            "🔍 Не удалось найти документацию. Подключаю ИИ-помощника..."
        )
        await handle_ai_with_context(message, query, state)

async def process_new_query(message: Message, text: str, state: FSMContext):
    """Обрабатывает новый запрос (не уточнение)"""
    # Сбрасываем счетчик уточнений и флаг
    await state.update_data(
        clarification_count=0,
        waiting_clarification=False,
        original_query=text
    )
    
    # Определяем тип запроса
    use_ai_directly = should_use_ai_improved(text)
    
    if use_ai_directly:
        await handle_ai_with_context(message, text, state)
    else:
        await handle_search_with_context(message, text, state)

async def process_combined_query(message: Message, query: str, state: FSMContext):
    """Обрабатывает объединенный запрос (исходный + уточнение)"""
    
    # Сохраняем обновленный запрос
    await state.update_data(original_query=query)
    
    # Определяем тип запроса
    use_ai_directly = should_use_ai_improved(query)
    
    if use_ai_directly:
        # Используем ИИ для сложных технических вопросов
        await handle_ai_with_context(message, query, state)
    else:
        # Используем поиск для документации
        await handle_search_with_context(message, query, state)

# --- Основной поиск ---
@dp.message()
async def handle_document_request(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text:
        return

    # Проверяем, не ожидаем ли мы уточнения
    data = await state.get_data()
    waiting_clarification = data.get("waiting_clarification", False)
    
    if waiting_clarification:
        # Это уточнение к предыдущему запросу
        await handle_clarification_message(message, text, state)
        return

    # Проверяем приветствия
    if text.lower().strip(".,!?") in GREETINGS:
        await message.answer(
            "Здравствуйте! 👋\n\n"
            "Используйте кнопки ниже или напишите запрос вручную — я с радостью помогу!",
            reply_markup=main_reply_keyboard
        )
        return

    # Проверяем кнопки
    if text in ["📚 База документации", "🎓 Обучающие материалы", "📞 Тех. специалист"]:
        return

    # Обрабатываем как новый запрос
    await process_new_query(message, text, state)

async def handle_clarification_message(message: Message, clarification: str, state: FSMContext):
    """Обрабатывает уточнение к предыдущему запросу"""
    data = await state.get_data()
    original_query = data.get("original_query", "")
    
    if not original_query:
        await message.answer("❌ Не удалось найти исходный запрос. Пожалуйста, задайте вопрос заново.")
        await state.clear()
        return
    
    # Объединяем исходный запрос с уточнением
    combined_query = f"{original_query} {clarification}"
    
    await message.answer(f"🔍 Анализирую уточненный запрос: <b>{combined_query}</b>", parse_mode="HTML")
    
    # Сбрасываем флаг ожидания уточнения
    await state.update_data(waiting_clarification=False)
    
    # Обрабатываем объединенный запрос
    await process_combined_query(message, combined_query, state)

# Обработчики для кнопок "Да/Нет"
@dp.callback_query(lambda c: c.data.startswith("info_helpful:"))
async def handle_info_helpful_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    action = callback.data.split(":")[1]
    data = await state.get_data()
    original_query = data.get("original_query", "запрос")
    clarification_count = data.get("clarification_count", 0)
    
    if action == "yes":
        response_text = "Спасибо что воспользовались HDL Assistant! 🎉"
        
        await callback.message.answer(
            response_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search")]
            ])
        )
        
        # Очищаем состояние диалога
        await state.clear()
        
    elif action == "no":
        clarification_count += 1
        
        if clarification_count <= 2:  # Максимум 2 попытки уточнения
            # Предлагаем уточнить текущий запрос
            response_text = (
                "Давайте уточним ваш запрос! 🤔\n\n"
                f"Ваш исходный вопрос: <b>«{original_query}»</b>\n\n"
                "Напишите дополнительные детали или уточнения прямо в чат..."
            )
            
            await callback.message.answer(
                response_text,
                parse_mode="HTML"
            )
            
            # Сохраняем состояние для продолжения диалога
            await state.update_data(
                clarification_count=clarification_count,
                waiting_clarification=True,
                original_query=original_query
            )
            
        else:
            # После двух попыток - предлагаем специалиста
            response_text = (
                "Похоже, мне не удалось помочь с вашим вопросом. 😔\n\n"
                "Рекомендую обратиться к техническому специалисту - он сможет дать точный ответ!"
            )
            
            await callback.message.answer(
                response_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📞 Связаться со специалистом", callback_data="support_form")],
                    [InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search")]
                ])
            )
            await state.clear()
    
    # Удаляем старые кнопки после нажатия
    await callback.message.edit_reply_markup(reply_markup=None)

# Обработчик для кнопки "Спросить у ИИ"
@dp.callback_query(lambda c: c.data == "ask_ai_current")
async def handle_ask_ai_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data = await state.get_data()
    original_query = data.get("original_query", "")
    
    if not original_query:
        await callback.message.answer("❌ Не удалось найти запрос. Пожалуйста, задайте вопрос заново.")
        return
    
    thinking_msg = await callback.message.answer("🤔 Анализирую ваш вопрос...")
    
    await state.update_data(original_query=original_query)
    
    # Извлекаем бренды из запроса для контекста
    brands_context = extract_brands_from_query(original_query)
    context = (
        "Ты эксперт по технической документации оборудования умного дома. "
        f"Бренды: {brands_context if brands_context else 'HDL, Buspro, Matech, URRI, Yeelight Pro, CoolAutomation, iOT Systems'}. "
        "ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. "
        "Не используй английский язык в ответах. "
        "Отвечай кратко и по делу. Если не знаешь ответа - предложи связаться со специалистом."
    )
    
    ai_response = await ask_ai(original_query, context=context)
    
    await thinking_msg.edit_text(
        f"🧠 {ai_response}\n\n"
        f"Полученная информация вам помогла?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="info_helpful:yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="info_helpful:no")
            ]
        ])
    )

# Обработчики для дополнительных кнопок
@dp.callback_query(lambda c: c.data == "new_search")
async def handle_new_search_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔍 Напишите ваш новый запрос и я с радостью помогу!")

@dp.callback_query(lambda c: c.data == "support_form")
async def support_form_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Пожалуйста, укажите ваше ФИО:")
    await state.set_state(SupportForm.name)

async def on_startup(bot: Bot, base_url: str):
    """Установка вебхука при старте"""
    if base_url:
        webhook_url = f"{base_url}/webhook"
        await bot.set_webhook(webhook_url)
        logging.info(f"Webhook установлен: {webhook_url}")

async def on_shutdown(bot: Bot):
    """Удаление вебхука при остановке"""
    await bot.delete_webhook()
    logging.info("Webhook удален")

def main():
    """Запуск приложения"""
    if RENDER_EXTERNAL_URL:
        # Режим вебхука для продакшена
        app = web.Application()
        
        # Регистрируем обработчик вебхука
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path="/webhook")
        
        # Настраиваем приложение
        setup_application(app, dp, bot=bot)
        
        # Запускаем на старте установку вебхука
        async def on_startup_app(app):
            await on_startup(bot, RENDER_EXTERNAL_URL)
        
        app.on_startup.append(on_startup_app)
        app.on_shutdown.append(on_shutdown)
        
        # Запускаем сервер
        web.run_app(app, host="0.0.0.0", port=PORT)
    else:
        # Режим polling для разработки
        async def run_polling():
            await dp.start_polling(bot)
        
        asyncio.run(run_polling())

if __name__ == "__main__":
    main()