from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Metrics")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="What do you want to do?"
)