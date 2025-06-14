import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.config import API_TOKEN
from handlers import routers
from ml.train_lstm import train_all_models
from logic.alerts import alerts_task
import logging              

async def auto_retrain_task():
    while True:
        try:
            train_all_models(
                window_size=20,
                horizon=60,
                epochs=140,
                batch_size=16
            )
            logging.info("✅ Auto-training completed")
        except Exception as e:
            logging.exception(f"❌ Auto-training error: {e}")
        await asyncio.sleep(60 * 60)

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    for r in routers:
        dp.include_router(r)

    asyncio.create_task(auto_retrain_task())
    logging.info("🚀 Auto-training scheduler started")

    asyncio.create_task(alerts_task(bot))
    logging.info("🚨 Alert scheduler started")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
