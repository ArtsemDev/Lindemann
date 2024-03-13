from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_panel_rkb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
    keyboard=[
        [
            KeyboardButton(text="МОИ ЗАДАЧИ 📋"),
            KeyboardButton(text="СОЗДАТЬ ЗАДАЧУ 📝"),
        ]
    ],
)
