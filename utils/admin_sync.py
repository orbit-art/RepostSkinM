from aiogram import Bot
from database import Database
import logging

logger = logging.getLogger(__name__)


async def delete_admin_messages(bot: Bot, db: Database, submission_id: int):
    messages = await db.get_admin_messages(submission_id)
    for admin_id, msg_id in messages.items():
        try:
            await bot.delete_message(chat_id=int(admin_id), message_id=msg_id)
        except Exception as e:
            logger.warning(f"Delete error: {e}")
