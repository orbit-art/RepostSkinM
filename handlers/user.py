import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ContentType
from keyboards import moderation_kb
from database import Database

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я — твой помощник для репостов в канал \"Посты СкинМейкеров\" 😊\n"
        "Отправь мне свой пост, и я передам его на модерацию 📄"
    )


@router.message(F.content_type.in_({
    ContentType.TEXT,
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.VIDEO_NOTE,
    ContentType.DOCUMENT,
}))
async def handle_submission(message: Message, db: Database):
    submission_id = await db.create_submission(
        message.from_user.id,
        message.message_id,
        message.content_type,
        message.media_group_id,
    )

    await message.answer("Ваш пост на модерации ⏳")

    admins = await db.get_active_admins()
    for admin_id in admins:
        try:
            sent = await message.forward(admin_id)
            kb = moderation_kb(submission_id)
            mod_msg = await sent.reply("Модерация:", reply_markup=kb)
            await db.set_admin_message(submission_id, admin_id, mod_msg.message_id)
        except Exception as e:
            logger.error(f"Forward error: {e}")
