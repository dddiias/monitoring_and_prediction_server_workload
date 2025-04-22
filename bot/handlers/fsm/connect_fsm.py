from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import uuid

from config.config import SERVER_IP
from logic.telegraf import generate_telegraf_config
from logic.storage import add_server
from aiogram.types import FSInputFile

import os

router = Router()

class ConnectServerFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_os = State()


@router.message(F.text == "📍 Подключить сервер")
async def start_server_connection(message: Message, state: FSMContext):
    await message.answer("🖥 Введите название сервера:")
    await state.set_state(ConnectServerFSM.waiting_for_name)


@router.message(ConnectServerFSM.waiting_for_name)
async def enter_server_name(message: Message, state: FSMContext):
    await state.update_data(server_name=message.text)
    await message.answer("💻 Укажите операционную систему сервера (например, Ubuntu 22.04):")
    await state.set_state(ConnectServerFSM.waiting_for_os)


@router.message(ConnectServerFSM.waiting_for_os)
async def enter_os_info(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    token = str(uuid.uuid4())
    data = await state.get_data()

    server_name = data["server_name"]
    os_info = message.text

    add_server(user_id, token, server_name=server_name, os_info=os_info)

    config_text = generate_telegraf_config(token, SERVER_IP)
    filename = "telegraf.conf"
    with open(filename, "w") as f:
        f.write(config_text)

    await message.answer_document(FSInputFile(filename), caption="⬆️ Telegraf конфигурация с уникальным токеном ⬆️")
    os.remove(filename)

    await message.answer(
        f"✅ Сервер <b>{server_name}</b> на <b>{os_info}</b> успешно подключён!\n\n"
        "📦 Инструкция по установке Telegraf:\n\n"
        "1️⃣ Установите Telegraf:\n"
        "<code>sudo apt update && sudo apt install telegraf</code>\n\n"
        "2️⃣ Замените конфиг:\n"
        "<code>sudo nano /etc/telegraf/telegraf.conf</code>\n"
        "и вставьте содержимое файла выше\n\n"
        "3️⃣ Перезапуск:\n"
        "<code>sudo systemctl restart telegraf</code>\n\n"
        "✅ Метрики начнут поступать автоматически.",
        parse_mode="HTML"
    )

    await state.clear()
