from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📚 База документации"),
            KeyboardButton(text="🎓 Обучающие материалы")
        ],
        [
            KeyboardButton(text="📞 Тех. специалист")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False  
)

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