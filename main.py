                        #    2 version HDL BOT



# import asyncio
# import logging
# import sys
# import os
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
# from dotenv import load_dotenv

# from bot.utils.yandex_disk_client import search_in_file_index, build_docs_url
# from bot.utils.ai_fallback import ask_qwen

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# YANDEX_DISK_FOLDER_PATH = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
# YANDEX_DISK_PUBLIC_KEY = os.getenv("YANDEX_DISK_PUBLIC_KEY")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# if not BOT_TOKEN:
#     raise ValueError("❌ BOT_TOKEN не найден в .env")
# if not YANDEX_DISK_PUBLIC_KEY:
#     raise ValueError("❌ YANDEX_DISK_PUBLIC_KEY не найден в .env")
# if not OPENROUTER_API_KEY:
#     raise ValueError("❌ OPENROUTER_API_KEY не найден в .env")

# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
# bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher()

# # ✅ Функция клавиатуры — ВНЕ обработчика!
# def get_support_keyboard() -> InlineKeyboardMarkup:
#     button = InlineKeyboardButton(
#         text="📞 Связаться с тех. специалистом",
#         url="https://t.me/hdl_support"  
#     )
#     return InlineKeyboardMarkup(inline_keyboard=[[button]])

# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     await message.answer(
#         "Привет!👨‍💻 Я HDL Assistant помогу найти любую техническую документацию.\n\n"
#         "Просто напишите запрос, например:\n"
#         "<i>Buspro MDL64-BP.53</i>\n"
#         "<i>HDL DALI контроллер</i>\n"
#         "<i>Matech датчик движения</i>"
#     )

# @dp.message()
# async def handle_document_request(message: Message) -> None:  
#     user_query = message.text.strip()
#     if not user_query:
#         await message.answer("Пожалуйста, введите запрос.")
#         return

#     await message.answer(f"🔍 Ищу документацию по: <b>{user_query}</b>")

#     results = search_in_file_index(user_query)

#     if results:
#         best = results[0]
#         try:
#             direct_link = build_docs_url(best["path"])
#             await message.answer(
#                 f"✅ Найдена документация:\n<b>{best['name']}</b>\n\n"
#                 f"🔗 Прямая ссылка на PDF:\n{direct_link}"
#             )
#         except Exception as e:
#             base = YANDEX_DISK_FOLDER_PATH.rstrip("/")
#             relative_path = (
#                 best["path"][len(base):].lstrip("/")
#                 if best["path"].startswith(base)
#                 else best["path"].lstrip("/")
#             )
#             await message.answer(
#                 f"✅ Найдена документация:\n<b>{best['name']}</b>\n\n"
#                 f"📁 Путь в папке:\n<code>{relative_path}</code>\n\n"
#                 f"🔗 Общая папка: https://disk.360.yandex.ru/d/{YANDEX_DISK_PUBLIC_KEY}"
#             )
#     else:
#         thinking_msg = await message.answer("🧠 ИИ думает... Подождите немного.")
#         context_brands = "HDL, Buspro, Matech, URRI, Yeelight Pro, CoolAutomation, iOT Systems"
#         ai_response = await ask_qwen(user_query, context=context_brands)
#         await thinking_msg.edit_text(
#             f"🔍 Документация не найдена. ИИ 👨‍💻 отвечает:\n\n{ai_response}",
#             reply_markup=get_support_keyboard()
#         )

# async def main() -> None:
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())


                                       #    3 version HDL BOT


# import asyncio
# import logging
# import sys
# import os
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.context import FSMContext
# from dotenv import load_dotenv

# from bot.utils.yandex_disk_client import search_in_file_index, build_docs_url
# from bot.utils.ai_fallback import ask_qwen

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# YANDEX_DISK_FOLDER_PATH = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
# YANDEX_DISK_PUBLIC_KEY = os.getenv("YANDEX_DISK_PUBLIC_KEY")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# if not BOT_TOKEN:
#     raise ValueError("❌ BOT_TOKEN не найден в .env")
# if not YANDEX_DISK_PUBLIC_KEY:
#     raise ValueError("❌ YANDEX_DISK_PUBLIC_KEY не найден в .env")
# if not OPENROUTER_API_KEY:
#     raise ValueError("❌ OPENROUTER_API_KEY не найден в .env")

# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
# bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher()

# # --- FSM для формы поддержки ---
# class SupportForm(StatesGroup):
#     name = State()
#     phone = State()

# # --- Клавиатуры ---
# def get_support_keyboard() -> InlineKeyboardMarkup:
#     """Кнопка для начала заполнения формы."""
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="📞 Связаться с тех. специалистом", callback_data="support_form")]
#     ])

# def get_chat_button() -> InlineKeyboardMarkup:
#     """Кнопка перехода в чат после отправки данных."""
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="💬 Написать специалисту", url="https://t.me/hdl_support")]
#     ])

# # --- Обработчики ---
# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     await message.answer(
#         "Привет!👨‍💻 Я HDL Assistant помогу найти любую техническую документацию.\n\n"
#         "Просто напишите запрос, например:\n"
#         "<i>Buspro MDL64-BP.53</i>\n"
#         "<i>HDL DALI контроллер</i>\n"
#         "<i>Matech датчик движения</i>"
#     )

# @dp.callback_query(lambda c: c.data == "support_form")
# async def support_form_start(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     await callback.message.answer("Пожалуйста, укажите ваше ФИО:")
#     await state.set_state(SupportForm.name)

# @dp.message(SupportForm.name)
# async def process_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await message.answer("Укажите ваш номер телефона (например, +7 999 123-45-67):")
#     await state.set_state(SupportForm.phone)

# @dp.message(SupportForm.phone)
# async def process_phone(message: Message, state: FSMContext):
#     phone = message.text
#     data = await state.get_data()
#     name = data["name"]

#     # Формируем сообщение для отправки в поддержку
#     support_text = (
#         f"📩 Новая заявка от пользователя:\n\n"
#         f"👤 ФИО: {name}\n"
#         f"📱 Телефон: {phone}\n"
#         f"🆔 ID: {message.from_user.id}\n"
#         f"🔗 @ {message.from_user.username or 'нет username'}"
#     )

#     # Отправляем в чат поддержки (если это публичный канал/группа, где бот админ)
#     try:
#         await bot.send_message(chat_id="-1003044266223", text=support_text)
#     except Exception as e:
#         # Если не получилось — логируем и отправляем админу (опционально)
#         print(f"Ошибка отправки в группу: {e}")
#         # Можно добавить отправку вам по ID, если нужно

#     # Отправляем пользователю кнопку для перехода
#     await message.answer(
#         "✅ Ваша заявка отправлена!\n\n"
#         "Теперь вы можете написать напрямую специалисту:",
#         reply_markup=get_chat_button()
#     )
#     await state.clear()

# @dp.message()
# async def handle_document_request(message: Message) -> None:
#     user_query = message.text.strip()
#     if not user_query:
#         await message.answer("Пожалуйста, введите запрос.")
#         return

#     await message.answer(f"🔍 Ищу документацию по: <b>{user_query}</b>")

#     results = search_in_file_index(user_query)

#     if results:
#         best = results[0]
#         try:
#             direct_link = build_docs_url(best["path"])
#             await message.answer(
#                 f"✅ Найдена документация:\n<b>{best['name']}</b>\n\n"
#                 f"🔗 Прямая ссылка на PDF:\n{direct_link}"
#             )
#         except Exception as e:
#             base = YANDEX_DISK_FOLDER_PATH.rstrip("/")
#             relative_path = (
#                 best["path"][len(base):].lstrip("/")
#                 if best["path"].startswith(base)
#                 else best["path"].lstrip("/")
#             )
#             await message.answer(
#                 f"✅ Найдена документация:\n<b>{best['name']}</b>\n\n"
#                 f"📁 Путь в папке:\n<code>{relative_path}</code>\n\n"
#                 f"🔗 Общая папка: https://disk.360.yandex.ru/d/{YANDEX_DISK_PUBLIC_KEY}"
#             )
#     else:
#         thinking_msg = await message.answer("🧠 ИИ думает... Подождите немного.")
#         context_brands = "HDL, Buspro, Matech, URRI, Yeelight Pro, CoolAutomation, iOT Systems"
#         ai_response = await ask_qwen(user_query, context=context_brands)
#         await thinking_msg.edit_text(
#             f"🔍 Документация не найдена. ИИ 👨‍💻 отвечает:\n\n{ai_response}",
#             reply_markup=get_support_keyboard()
#         )

# # --- Запуск ---
# async def main() -> None:
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())






# import asyncio
# import logging
# import sys
# import os
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.context import FSMContext
# from dotenv import load_dotenv

# from bot.utils.yandex_disk_client import search_in_file_index, build_docs_url
# from bot.utils.ai_fallback import ask_qwen

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# YANDEX_DISK_FOLDER_PATH = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
# YANDEX_DISK_PUBLIC_KEY = os.getenv("YANDEX_DISK_PUBLIC_KEY")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# if not BOT_TOKEN:
#     raise ValueError("❌ BOT_TOKEN не найден в .env")
# if not YANDEX_DISK_PUBLIC_KEY:
#     raise ValueError("❌ YANDEX_DISK_PUBLIC_KEY не найден в .env")
# if not OPENROUTER_API_KEY:
#     raise ValueError("❌ OPENROUTER_API_KEY не найден в .env")

# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
# bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher()

# # --- FSM для формы поддержки ---
# class SupportForm(StatesGroup):
#     name = State()
#     phone = State()
#     original_query = State()  # Сохраняем исходный вопрос

# # --- Клавиатуры ---
# def get_support_keyboard() -> InlineKeyboardMarkup:
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="📞 Связаться с тех. специалистом", callback_data="support_form")]
#     ])

# def get_chat_button() -> InlineKeyboardMarkup:
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="💬 Написать специалисту", url="https://t.me/hdl_support")]
#     ])

# # --- Обработчики ---
# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     await message.answer(
#         "Привет!👨‍💻 Меня зовут HDL Assistant и я здесь для того, чтобы технические вопросы решались легко и быстро.\n\n"
#         "Запутались в документации? Нужна спецификация или мануал? Я с радостью помогу!\n"
#     )

# @dp.callback_query(lambda c: c.data == "support_form")
# async def support_form_start(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     await callback.message.answer("Пожалуйста, укажите ваше ФИО:")
#     await state.set_state(SupportForm.name)

# @dp.message(SupportForm.name)
# async def process_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await message.answer("Укажите ваш номер телефона (например, +7 999 123-45-67):")
#     await state.set_state(SupportForm.phone)

# @dp.message(SupportForm.phone)
# async def process_phone(message: Message, state: FSMContext):
#     phone = message.text
#     data = await state.get_data()
#     name = data["name"]
#     original_query = data.get("original_query", "Запрос не сохранён")

#     support_text = (
#         f"📩 Новая заявка от пользователя:\n\n"
#         f"👤 ФИО: {name}\n"
#         f"📱 Телефон: {phone}\n"
#         f"🆔 ID: {message.from_user.id}\n"
#         f"🔗 @ {message.from_user.username or 'нет username'}\n\n"
#         f"❓ Вопрос пользователя:\n{original_query}"
#     )

#     # Отправка в группу поддержки
#     GROUP_CHAT_ID = -1003044266223 
#     try:
#         await bot.send_message(chat_id=-1003044266223, text=support_text)
#     except Exception as e:
#         print(f"Ошибка отправки в группу: {e}")
#         await message.answer("Не удалось отправить заявку. Попробуйте позже.")
#         await state.clear()
#         return

#     await message.answer(
#         "✅ Ваша заявка отправлена!\n\n"
#         "Специалист свяжется с вами в ближайшее время.",
#         reply_markup=get_chat_button()
#     )
#     await state.clear()

# @dp.message()
# async def handle_document_request(message: Message, state: FSMContext) -> None:
#     user_query = message.text.strip()
#     if not user_query:
#         await message.answer("Пожалуйста, введите запрос.")
#         return

#     await message.answer(f"🔍 Уже ищу! Один момент... 👨‍💻: <b>{user_query}</b>")

#     results = search_in_file_index(user_query)

#     if results:
#         best = results[0]
#         try:
#             direct_link = build_docs_url(best["path"])
#             await message.answer(
#                 f"✅ Найдена документация:\n<b>{best['name']}</b>\n\n"
#                 f"🔗 Прямая ссылка на PDF:\n{direct_link}"
#             )
#         except Exception as e:
#             base = YANDEX_DISK_FOLDER_PATH.rstrip("/")
#             relative_path = (
#                 best["path"][len(base):].lstrip("/")
#                 if best["path"].startswith(base)
#                 else best["path"].lstrip("/")
#             )
#             await message.answer(
#                 f"✅ Найдена документация:\n<b>{best['name']}</b>\n\n"
#                 f"📁 Путь в папке:\n<code>{relative_path}</code>\n\n"
#                 f"🔗 Общая папка: https://disk.360.yandex.ru/d/{YANDEX_DISK_PUBLIC_KEY}"
#             )
#     else:
#         thinking_msg = await message.answer("Сортирую информацию по полочкам... Сейчас всё объясню! 🗂️")
#         context_brands = "HDL, Buspro, Matech, URRI, Yeelight Pro, CoolAutomation, iOT Systems"
#         ai_response = await ask_qwen(user_query, context=context_brands)
        
#         # Сохраняем исходный запрос для формы поддержки
#         await state.update_data(original_query=user_query)
        
#         await thinking_msg.edit_text(
#             f"🔍 Вот что я нашёл:\n\n{ai_response}",
#             reply_markup=get_support_keyboard()
#         )

# # --- Запуск ---
# async def main() -> None:
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())

# Версия от 08.10.2025
import os
import asyncio
import logging
import sys
import re
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
from keyboards import main_reply_keyboard, docs_inline_keyboard

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

async def handle_ai_directly(message: Message, text: str, state: FSMContext):
    """
    Обрабатывает запросы, которые сразу идут к ИИ
    """
    thinking_msg = await message.answer("Сортирую информацию по полочкам... Сейчас всё объясню! 🗂️")
    
    await state.update_data(original_query=text)
    
    query_lower = text.lower()
    
    # Улучшенный контекст для интеграции Алисы с KNX
    if any(keyword in query_lower for keyword in ["алис", "голосов", "alisa"]):
        context = (
            "Ты технический эксперт по интеграции систем умного дома. "
            "ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. "
            "Не используй английский язык в ответах. "
            
            "Интеграция Яндекс Алисы с системами KNX:\n"
            "1. Требуется шлюз или контроллер с поддержкой голосового управления\n"
            "2. HDL предлагает решения для интеграции через Smart Gateway\n" 
            "3. Необходимо настроить навык Алисы для работы с оборудованием\n"
            "4. KNX - проводной протокол, требуется совместимое оборудование\n\n"
            
            "Возможные решения:\n"
            "- HDL Smart Gateway с поддержкой голосового управления\n"
            "- Шлюзы Buspro с интеграцией Алисы\n" 
            "- Специальные контроллеры с поддержкой KNX и облачных сервисов\n"
            "- Настройка через приложение HDL Smart\n\n"
            
            "Если нужны конкретные модели или инструкции - предложи связаться со специалистом."
        )
    else:
        context = (
            "Ты эксперт по технической документации оборудования умного дома. "
            "Бренды: HDL, Buspro, Matech, URRI, Yeelight Pro, CoolAutomation, iOT Systems. "
            "ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. "
            "Не используй английский язык в ответах. "
            "Отвечай кратко и по делу. Если не знаешь ответа - предложи связаться со специалистом."
        )
    
    ai_response = await ask_ai(text, context=context)
    
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

# --- Основной поиск ---
@dp.message()
async def handle_document_request(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text:
        return

    if text.lower().strip(".,!?") in GREETINGS:
        await message.answer(
            "Здравствуйте! 👋\n\n"
            "Используйте кнопки ниже или напишите запрос вручную — я с радостью помогу!",
            reply_markup=main_reply_keyboard
        )
        return

    if text in ["📚 База документации", "🎓 Обучающие материалы", "📞 Тех. специалист"]:
        return

    query_lower = text.lower()

    # ВАЖНОЕ ИЗМЕНЕНИЕ: Теперь запросы про Алису идут в обычный поиск для получения ссылки
    if "алис" in text.lower() and ("knx" in text.lower() or "подключи" in text.lower() or "интеграци" in text.lower()):
        print("🎯 ОБНОВЛЕННО: Запрос про Алису → обычный поиск (для ссылки на документацию)")
        # Продолжаем обычный поиск - не переходим к ИИ

    # Проверяем, нужно ли сразу подключать ИИ
    use_ai_directly = should_use_ai_directly(text)
    print(f"🎯 Финальное решение для '{text}': {'ИИ' if use_ai_directly else 'поиск'}")

    if use_ai_directly:
        await handle_ai_directly(message, text, state)
        return

    # Обычный поиск для других запросов
    results = await smart_document_search(text)

    if results:
        # Проверяем, является ли результат ссылкой на папку
        if len(results) == 1 and results[0].get("is_folder_link"):
            folder_link = results[0].get("folder_link")
            await message.answer(
                f"📁 <b>Документация по запросу: {text}</b>\n\n"
                f"Для просмотра всей документации перейдите по ссылке:\n"
                f"🔗 <a href='{folder_link}'>Открыть папку на Яндекс.Диске</a>\n\n"
                f"В папке вы найдете все доступные документы, инструкции и технические паспорта.",
                parse_mode="HTML"
            )
            return
        
        # Стандартный вывод результатов поиска
        response = f"🔍 Ищу документацию по: <b>{text}</b>\n\n"
        response += f"✅ Найдено документов: {len(results)}\n\n"
        
        for i, file_data in enumerate(results[:3], 1):
            try:
                # СПЕЦИАЛЬНАЯ ССЫЛКА ДЛЯ КАБЕЛЯ KNX YE00820
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
        
        # Только кнопки Да/Нет (без кнопок документов)
        await message.answer(
            response,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Да", callback_data="info_helpful:yes"),
                    InlineKeyboardButton(text="❌ Нет", callback_data="info_helpful:no")
                ]
            ]),
            parse_mode="HTML"  # Важно для кликабельных ссылок!
        )
        
        # Если нашли только технические паспорта для сложного запроса
        if len(results) == 1 and has_only_technical_files(results):
            await message.answer(
                "🤔 Кажется, это техническая документация, а не руководство по интеграции.\n\n"
                "Могу подключить ИИ-помощника для более точного ответа:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🧠 Спросить у ИИ", callback_data=f"ask_ai:{text}")]
                ])
            )
        
    else:
        # Если документы не найдены - подключаем ИИ
        await handle_ai_directly(message, text, state)

# Обработчики для кнопок "Да/Нет"
@dp.callback_query(lambda c: c.data.startswith("info_helpful:"))
async def handle_info_helpful_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    action = callback.data.split(":")[1]
    data = await state.get_data()
    original_query = data.get("original_query", "запрос")
    
    if action == "yes":
        response_text = "Спасибо что воспользовались HDL Assistant! 🎉"
        
        # Только кнопка "Новый поиск"
        await callback.message.answer(
            response_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search")]
            ])
        )
        
    elif action == "no":
        response_text = "Уточните запрос - я с радостью помогу! 💡"
        
        # Если пользователь уже нажимал "Нет" ранее - показываем кнопки
        user_data = await state.get_data()
        if user_data.get('already_clicked_no'):
            await callback.message.answer(
                response_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🔄 Уточнить запрос", callback_data=f"ask_ai:{original_query}"),
                        InlineKeyboardButton(text="📞 Специалист", callback_data="support_form")
                    ]
                ])
            )
        else:
            # Первое нажатие "Нет" - без кнопок
            await callback.message.answer(response_text)
            await state.update_data(already_clicked_no=True)
    
    # Удаляем старые кнопки после нажатия
    await callback.message.edit_reply_markup(reply_markup=None)

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

# Обработчик для кнопки "Спросить у ИИ"
@dp.callback_query(lambda c: c.data.startswith("ask_ai:"))
async def handle_ask_ai_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    query = callback.data.replace("ask_ai:", "")
    thinking_msg = await callback.message.answer("Сортирую информацию по полочкам... Сейчас всё объясню! 🗂️")
    
    await state.update_data(original_query=query)
    
    # Контекст с требованием отвечать только на русском
    context = (
        "Ты эксперт по технической документации оборудования умного дома. "
        "Бренды: HDL, Buspro, Matech, URRI, Yeelight Pro, CoolAutomation, iOT Systems. "
        "ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. "
        "Не используй английский язык в ответах. "
        "Отвечай кратко и по делу. Если не знаешь ответа - предложи связаться со специалистом."
    )
    
    ai_response = await ask_ai(query, context=context)
    
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