import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db
from handlers.start import router as start_router
from handlers.vpn import router as vpn_router
from handlers.games import router as games_router
from handlers.referrals import router as ref_router
from handlers.promo import router as promo_router
from handlers.admin import router as admin_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

bot = Bot(token=BOT_TOKEN)

async def main():
    init_db()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(vpn_router)
    dp.include_router(games_router)
    dp.include_router(ref_router)
    dp.include_router(promo_router)
    dp.include_router(admin_router)
    me = await bot.get_me()
    logging.info(f"✅ Бот запущен: @{me.username}")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
