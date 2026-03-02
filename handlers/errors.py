import logging
from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)
router = Router()


@router.errors()
async def global_error_handler(event: ErrorEvent):
    logger.exception(f"Unhandled error: {event.exception}")
