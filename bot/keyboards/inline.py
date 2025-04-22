from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_inline_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Подключить сервер", callback_data="get_config"),
        InlineKeyboardButton(text="📊 Показать метрики", callback_data="metrics"),]
        [InlineKeyboardButton(text="🔮 Прогноз", callback_data="predict"),
         InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")]
    ])

def get_settings_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Установить лимит CPU", callback_data="set_cpu_limit")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def get_help_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 О подключении", callback_data="help_connect")],
        [InlineKeyboardButton(text="📊 О метриках", callback_data="help_metrics")],
        [InlineKeyboardButton(text="🔮 О прогнозе", callback_data="help_forecast")],
        [InlineKeyboardButton(text="📄 О моих серверах", callback_data="help_myservers")],

    ])
