import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import load_config
from database import Database
from handlers import user, admin, errors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    config = load_config()
    db = Database(config.db_path)
    await db.connect()

    if await db.active_admin_count() == 0:
        await db.add_admin(config.main_admin_id, is_main=True)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(errors.router)

    dp["db"] = db

    active_count = await db.active_admin_count()
    logger.info(f"✅ Бот запущен! Канал: {config.channel_id}, Админов активно: {active_count}")

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
