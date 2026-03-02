from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def moderation_kb(submission_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"approve_{submission_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject_{submission_id}",
                ),
            ]
        ]
    )
