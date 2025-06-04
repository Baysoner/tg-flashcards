import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from handlers import register_handlers
from db import init_db

async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    await register_handlers(dp)

    await init_db()
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
