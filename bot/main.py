import asyncio
from aiogram import Bot, Dispatcher
from logic.config import API_TOKEN
from logic.handlers.handlers import router as start_router

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
