from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandStart


import logic.handlers.keyboards as kb
import uuid
import os

from logic.utils import generate_telegraf_config, get_metrics_from_server, format_metrics
from logic.config import SERVER_IP
from logic.storage import load_tokens, save_tokens

router = Router()
user_tokens = load_tokens()

@router.message(CommandStart())
async def handle_start(message: Message):
    user_id = str(message.from_user.id)

    if user_id in user_tokens:
        token = user_tokens[user_id]
    else:
        token = str(uuid.uuid4())
        user_tokens[user_id] = token
        save_tokens(user_tokens)

    config_text = generate_telegraf_config(token, SERVER_IP)
    filename = f"telegraf.conf"
    with open(filename, "w") as f:
        f.write(config_text)

    await message.answer("👋 Привет! Вот твой telegraf.conf с уникальным токеном. Скачай и вставь его в Telegraf.", reply_markup=kb.main)
    await message.answer_document(document=FSInputFile(filename))

    os.remove(filename)




@router.message(F.text == "Metrics")
async def handle_metrics(message: Message):
    user_id = str(message.from_user.id)
    token = user_tokens.get(user_id)

    if not token:
        await message.answer("Вы ещё не зарегистрированы. Отправьте /start.")
        return

    data = get_metrics_from_server(token, SERVER_IP)
    text = format_metrics(data)
    await message.answer(text)
    await message.answer(reply_markup=kb.main)