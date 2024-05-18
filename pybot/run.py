import asyncio
import os

from aiogram.enums import ParseMode
from dotenv import load_dotenv, find_dotenv
import utils.db
import logging
from aiogram import Bot, Dispatcher
from handlers import admin, menu


load_dotenv(find_dotenv(".env"))
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), parse_mode=ParseMode.HTML)
dp = Dispatcher()


async def main():
    dp.include_routers(admin.router, menu.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
