import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from scheduler import scheduler
from database.database import engine
from database.models import Base

from handlers import start, crypto, alert


load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


dp.include_router(start.router)
dp.include_router(alert.router)
dp.include_router(crypto.router)


def create_table():
    Base.metadata.create_all(bind=engine)


async def main():
    create_table()
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
