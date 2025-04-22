from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from logic.storage import load_users, delete_server

router = Router()

@router.message(F.text == "📄 Мои серверы")
async def list_servers(message: Message, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users or not users[user_id]["servers"]:
        await message.answer("❌ У вас нет подключённых серверов.")
        return

    response = ["📄 <b>Список ваших серверов:</b>\n"]
    for i, srv in enumerate(users[user_id]["servers"], start=1):
        response.append(
            f"{i}. <b>{srv['server_name']}</b> ({srv['os']})\n"
            f"📆 Подключён: {srv['connected_at']}\n"
            f"🔑 Token: <code>{srv['token']}</code>\n"
        )
    await message.answer("\n".join(response), parse_mode="HTML")


@router.message(F.text == "❌ Удалить сервер")
async def ask_delete_server(message: Message, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)
    users = load_users()

    servers = users.get(user_id, {}).get("servers", [])

    if not servers:
        await message.answer("❌ У вас нет серверов для удаления.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{srv['server_name']} ({srv['os']})",
                callback_data=f"delete:{srv['token']}")
            ] for srv in servers
        ]
    )

    await message.answer("Выберите сервер для удаления:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("delete:"))
async def confirm_delete(callback: CallbackQuery):
    token = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)

    if delete_server(user_id, token):
        await callback.message.edit_text("✅ Сервер успешно удалён.")
    else:
        await callback.message.edit_text("❌ Не удалось удалить сервер.")
