from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📚 База документации"),
            KeyboardButton(text="🎓 Обучающие материалы")
        ],
        [
            KeyboardButton(text="❓ FAQ: Часто Задаваемые Вопросы"),
            KeyboardButton(text="📞 Тех. специалист")
            
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False  
)

# FAQ: основное меню
faq_main_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1. Вопросы по ПО", callback_data="faq_software")],
    [InlineKeyboardButton(text="2. Вопросы по оборудованию", callback_data="faq_hardware")],
    [InlineKeyboardButton(text="3. Вопросы о сотрудничестве", callback_data="faq_partnership")],
    [InlineKeyboardButton(text="4. KNX", callback_data="faq_knx")],
    [InlineKeyboardButton(text="5. BusPro", callback_data="faq_buspro")],
    [InlineKeyboardButton(text="6. Приложения/интеграции", callback_data="faq_integrations")],
    [InlineKeyboardButton(text="7. Общие вопросы", callback_data="faq_general")]
])

# --- Подменю: 1. Вопросы по ПО ---
faq_software_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1. Софт", url="https://hdlautomation.ru/faq/voprosy-po-programmnomu-obespecheniyu/soft/")],
    [InlineKeyboardButton(text="2. Прошивки", url="https://hdlautomation.ru/faq/voprosy-po-programmnomu-obespecheniyu/proshivki/")],
    [InlineKeyboardButton(text="3. Отдельные вопросы по ПО", url="https://hdlautomation.ru/faq/voprosy-po-programmnomu-obespecheniyu/otdelnye-voprosy-po-programmnomu-obespecheniyu/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])


# --- Подменю: 2. Вопросы по оборудованию ---
faq_hardware_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1. Техническая Документация", url="https://hdlautomation.ru/faq/voprosy-po-oborudovaniyu/tekhnicheskaya-dokumentatsiya/")],
    [InlineKeyboardButton(text="2. Техническая Информация", url="https://hdlautomation.ru/faq/voprosy-po-oborudovaniyu/tekhnicheskaya-dokumentatsiya/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])

# --- Подменю: 3. Вопросы о сотрудничестве ---
faq_partnership_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1. Начало Сотрудничества", url="https://hdlautomation.ru/faq/voprosy-po-prodazham/kak-stat-nashim-partnerom-/")],
    [InlineKeyboardButton(text="2. Тренинги HDL Buspro", url="https://hdlautomation.ru/faq/voprosy-po-prodazham/treningi-hdl-buspro/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])

# --- Подменю: 4. KNX ---
faq_knx_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1. Шлюзы", url="https://hdlautomation.ru/faq/KNX/shlyuzy/")],
    [InlineKeyboardButton(text="2. Шинные соединители", url="https://hdlautomation.ru/faq/KNX/shinnye-soediniteli/")],
    [InlineKeyboardButton(text="3. Панели управления / клавишные устройства", url="https://hdlautomation.ru/faq/KNX/paneli-upravleniya-klavishnye-ustrojstva/")],
    [InlineKeyboardButton(text="4. Датчики", url="https://hdlautomation.ru/faq/KNX/datchiki/")],
    [InlineKeyboardButton(text="5. Управление освещением", url="https://hdlautomation.ru/faq/KNX/upravlenie-osveshcheniem/")],
    [InlineKeyboardButton(text="6. Управление отоплением", url="https://hdlautomation.ru/faq/KNX/upravlenie-otopleniem/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])

# --- Подменю: 5. BusPro ---
faq_buspro_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1. Датчики", url="https://hdlautomation.ru/faq/BusPro/datchiki/")],
    [InlineKeyboardButton(text="2. Шлюзы", url="https://hdlautomation.ru/faq/BusPro/shlyuzy/")],
    [InlineKeyboardButton(text="3. Панели управления", url="https://hdlautomation.ru/faq/BusPro/paneli-upravleniya/")],
    [InlineKeyboardButton(text="4. Сухие контакты", url="https://hdlautomation.ru/faq/BusPro/sukhie-kontakty/")],
    [InlineKeyboardButton(text="5. Управление освещением", url="https://hdlautomation.ru/faq/BusPro/upravlenie-osveshcheniem/")],
    [InlineKeyboardButton(text="6. Управление отоплением", url="https://hdlautomation.ru/faq/BusPro/upravlenie-otopleniem/")],
    [InlineKeyboardButton(text="7. Модуль логики", url="https://hdlautomation.ru/faq/BusPro/modul-logiki/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])


faq_integrations_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ответы на вопросы о приложениях / интеграции с голосовыми помощниками", url="https://hdlautomation.ru/faq/prilozheniya/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])


# --- Подменю: 6. Ответы на вопросы о приложениях ---

faq_integrations_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ответы на вопросы о приложениях / интеграции с голосовыми помощниками", url="https://hdlautomation.ru/faq/prilozheniya/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])

# --- Подменю: 7. Общие вопросы ---
faq_general_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Общие вопросы", url="https://hdlautomation.ru/faq/obshchie-voprosy/")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="faq_back_to_main")]
])



# База документации — инлайн-клавиатура с брендами
docs_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="iOT Systems", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/01.%20iOT%20Systems")],
    [InlineKeyboardButton(text="HDL", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/02.%20HDL")],
    [InlineKeyboardButton(text="Coolautomation", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/03.%20Coolautomation")],
    [InlineKeyboardButton(text="Insprid", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/04.%20Insprid")],
    [InlineKeyboardButton(text="Moorgen", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/05.%20Moorgen")],
    [InlineKeyboardButton(text="Yeelight Pro", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/06.%20Yeelight%20Pro")],
    [InlineKeyboardButton(text="Casa Tunes", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/07.%20CasaTunes")],
    [InlineKeyboardButton(text="Matech", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/08.%20Matech")],
    [InlineKeyboardButton(text="Creatrol", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/09.%20Creatrol%20%D1%81%D0%B5%D0%BD%D1%81%D0%BE%D1%80%D1%8B")],
    [InlineKeyboardButton(text="URRI", url="https://disk.360.yandex.ru/d/xJi6eEXBTq01sw/10.%20URRI.%20%D0%9F%D0%BB%D0%B5%D0%B5%D1%80%D1%8B%2C%20%D1%80%D0%B5%D1%81%D0%B8%D0%B2%D0%B5%D1%80%D1%8B")]
])