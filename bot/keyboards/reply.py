from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Подключить сервер"), KeyboardButton(text="📊 Метрики")],
        [KeyboardButton(text="📄 Мои серверы"), KeyboardButton(text="❌ Удалить сервер")],
        [KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)
