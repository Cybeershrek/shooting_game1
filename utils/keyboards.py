from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def game_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/status"), KeyboardButton(text="/solve")],
            [KeyboardButton(text="/shoot"), KeyboardButton(text="/heal")],
            [KeyboardButton(text="/help")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )