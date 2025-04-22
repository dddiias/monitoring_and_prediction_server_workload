from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from logic.storage import load_users
from config.config import SERVER_IP
from logic.metrics import get_metrics_from_server
from utils.formatters import format_metrics
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()


@router.message(F.text == "📊 Метрики")
async def choose_server(message: Message):

    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users or not users[user_id]["servers"]:
        await message.answer("У вас пока нет подключённых серверов.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{srv['server_name']} ({srv['os']})",
                callback_data=f"metrics:{srv['token']}")]
            for srv in users[user_id]["servers"]
        ]
    )

    await message.answer("Выберите сервер для просмотра метрик:", reply_markup=kb)


@router.callback_query(F.data.startswith("metrics:"))
async def send_metrics(callback: CallbackQuery):
    token = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)
    users = load_users()

    server_info = None
    for srv in users.get(user_id, {}).get("servers", []):
        if srv["token"] == token:
            server_info = srv
            break

    if not server_info:
        await callback.message.edit_text("❌ Сервер не найден.")
        return

    data = get_metrics_from_server(token, SERVER_IP)
    text = f"<b>📊 Метрики сервера:</b> {server_info['server_name']} ({server_info['os']})\n\n" + format_metrics(data)

    await callback.message.edit_text(text, parse_mode="HTML")
