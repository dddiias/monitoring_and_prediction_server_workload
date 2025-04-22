import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.config import API_TOKEN
from handlers import routers

async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    for r in routers:
        dp.include_router(r)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
