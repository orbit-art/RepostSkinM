from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from database import Database
from utils.admin_sync import delete_admin_messages
from config import load_config

router = Router()
config = load_config()


@router.message(F.text.startswith("/add_admin"))
async def add_admin_cmd(message: Message, db: Database):
    if message.from_user.id != config.main_admin_id:
        return

    try:
        user_id = int(message.text.split()[1])
        await db.add_admin(user_id)
        await message.answer("Админ добавлен")
    except Exception:
        await message.answer("Ошибка формата")


@router.message(F.text == "/vacation")
async def vacation_cmd(message: Message, db: Database):
    admin = await db.get_admin(message.from_user.id)
    if not admin:
        return

    count = await db.active_admin_count()
    if count <= 1 and admin[2] == 0:
        await message.answer("Нельзя уйти в отпуск — не останется активных админов")
        return

    is_on_vacation = await db.toggle_vacation(message.from_user.id)

    if is_on_vacation:
        await message.answer("Вы в отпуске 🏖️ Заявки приходить не будут")
    else:
        await message.answer("С возвращением! 🎉 Заявки снова поступают")


@router.callback_query(F.data.startswith(("approve_", "reject_")))
async def moderation_action(callback: CallbackQuery, db: Database, bot):
    action, submission_id = callback.data.split("_")
    submission_id = int(submission_id)

    updated = await db.update_status_atomic(
        submission_id,
        "approved" if action == "approve" else "rejected"
    )

    if not updated:
        await callback.answer("Уже обработано", show_alert=True)
        return

    submission = await db.get_submission(submission_id)
    user_id = submission[1]
    message_id = submission[2]

    if action == "approve":
        await bot.forward_message(config.channel_id, user_id, message_id)
        await bot.send_message(user_id, "Ваш пост был принят и будет опубликован в ближайшее время! ✅")
    else:
        await bot.send_message(user_id, "К сожалению, Ваш пост не прошёл модерацию ❌")

    await delete_admin_messages(bot, db, submission_id)
    await callback.answer("Готово")
