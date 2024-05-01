import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import admin


logging.basicConfig(level=logging.INFO)
bot = Bot(token="6981223922:AAEt9MEmCLrZ0jlXP36TJRQf7iFKcZ7KG4Y")
dp = Dispatcher()


async def main():
    dp.include_router(admin.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
