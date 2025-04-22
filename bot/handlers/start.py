from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.reply import main_menu


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message):
    await message.answer(
        "👋 Привет! Добро пожаловать в систему мониторинга и прогнозирования серверной нагрузки.\n\n"
        "⚙️ Если ты готов начать, нажми кнопку <b>«📍 Подключить сервер»</b> ниже.",
        reply_markup=main_menu,
        parse_mode="HTML"
    )

