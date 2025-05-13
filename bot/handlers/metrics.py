from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from logic.storage import load_users
from logic.metrics import get_metrics_from_server
from logic.history import analyze_metrics
from utils.formatters import format_metrics

router = Router()

@router.message(F.text == "📊 Метрики")
async def choose_server(message: Message):
    user_id = str(message.from_user.id)
    users = load_users()
    servers = users.get(user_id, {}).get("servers", [])
    if not servers:
        await message.answer("У вас пока нет подключённых серверов.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{srv['server_name']} ({srv['os']})",
                    callback_data=f"metrics:{srv['token']}"
                )
            ]
            for srv in servers
        ]
    )
    await message.answer("Выберите сервер для просмотра метрик:", reply_markup=kb)


@router.callback_query(F.data.startswith("metrics:"))
async def send_metrics(callback: CallbackQuery):
    await callback.answer()
    token = callback.data.split(":", 1)[1]
    user_id = str(callback.from_user.id)
    servers = [srv["token"] for srv in load_users().get(user_id, {}).get("servers", [])]
    if token not in servers:
        await callback.message.edit_text("❌ Сервер не найден.")
        return

    data = get_metrics_from_server(token)
    stats = analyze_metrics(token)
    text = format_metrics(data, stats)

    warnings = []
    if stats["CPU"]["User"]["avg"] > 90:
        warnings.append("⚠ CPU в среднем выше 90%")
    if stats["Memory"]["Used"]["avg"] > 90:
        warnings.append("⚠ Память в среднем используется более 90%")
    if warnings:
        text += "\n\n" + "\n".join(warnings)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔮 Прогноз нагрузки",
                    callback_data=f"predict:{token}"
                )
            ]
        ]
    )
    await callback.message.edit_text(text, reply_markup=kb)
