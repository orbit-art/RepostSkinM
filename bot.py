import os
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '123456789').split(',')]
CHANNEL_ID = os.getenv('CHANNEL_ID', '@your_channel')

# Упрощенное хранилище
class Storage:
    def __init__(self):
        self.pending_posts = {}
        self.admin_vacations = {}

storage = Storage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def create_admin_keyboard(post_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{post_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{post_id}"))
    return keyboard.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("👋 Добро пожаловать, администратор!")
    else:
        await message.answer("👋 Отправьте мне пост для модерации!")

@dp.message(F.text)
async def handle_text_message(message: Message):
    if message.from_user.is_bot:
        return
        
    if is_admin(message.from_user.id):
        return
    
    await message.answer("⏳ Ваш текст отправлен на модерацию!")
    logger.info(f"Получен пост от пользователя {message.from_user.id}")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_post(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен.")
        return
        
    await callback.answer("✅ Пост одобрен!")
    await callback.message.edit_text("✅ Пост одобрен и опубликован!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_post(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен.")
        return
        
    await callback.answer("❌ Пост отклонен!")
    await callback.message.edit_text("❌ Пост отклонен!")

async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())        }
        self.pending_posts[forwarded_to_admin.message_id] = post_data
        self.user_posts[user_message.from_user.id] = forwarded_to_admin.message_id
        
    async def get_pending_post(self, admin_message_id: int) -> Optional[Dict]:
        return self.pending_posts.get(admin_message_id)
    
    async def remove_pending_post(self, admin_message_id: int):
        if admin_message_id in self.pending_posts:
            user_id = self.pending_posts[admin_message_id]['user_id']
            if user_id in self.user_posts:
                del self.user_posts[user_id]
            del self.pending_posts[admin_message_id]
    
    async def set_admin_vacation(self, admin_id: int, on_vacation: bool):
        self.admin_vacations[admin_id] = on_vacation
        
    async def is_admin_on_vacation(self, admin_id: int) -> bool:
        return self.admin_vacations.get(admin_id, False)
    
    async def get_available_admins_count(self) -> int:
        return len([admin_id for admin_id in ADMIN_IDS if not self.admin_vacations.get(admin_id, False)])

storage = Storage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdminStates(StatesGroup):
    waiting_for_channel = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def create_admin_keyboard(post_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{post_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{post_id}")
    )
    return keyboard.as_markup()

def create_vacation_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🛌 Уйти в отпуск", callback_data="vacation_on"),
        InlineKeyboardButton(text="↩️ Вернуться из отпуска", callback_data="vacation_off")
    )
    return keyboard.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if is_admin(message.from_user.id):
        await message.answer(
            "👋 Добро пожаловать, администратор!\n\n"
            "Доступные команды:\n"
            "/vacation - управление отпуском\n"
            "/set_channel - установить канал для публикации"
        )
    else:
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "Отправьте мне пост, и я перешлю его администраторам для модерации."
        )

@dp.message(Command("vacation"))
async def cmd_vacation(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return
        
    await message.answer(
        "🏖️ Управление отпуском:",
        reply_markup=create_vacation_keyboard()
    )

@dp.message(Command("set_channel"))
async def cmd_set_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return
        
    await message.answer(
        "📝 Отправьте ID или username канала (например: @channel_name):"
    )
    await state.set_state(AdminStates.waiting_for_channel)

@dp.message(AdminStates.waiting_for_channel)
async def process_channel_id(message: Message, state: FSMContext):
    global CHANNEL_ID
    CHANNEL_ID = message.text.strip()
    await state.clear()
    await message.answer(f"✅ Канал установлен: {CHANNEL_ID}")

@dp.message(F.content_type.in_({'text', 'photo', 'video', 'document'}))
async def handle_user_post(message: Message):
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return
        
    # Если это админ, обрабатываем как обычное сообщение
    if is_admin(message.from_user.id):
        return
    
    # Проверяем, есть ли активные администраторы
    available_admins = await storage.get_available_admins_count()
    if available_admins == 0:
        await message.answer("❌ В настоящее время нет доступных администраторов. Попробуйте позже.")
        return
    
    # Уведомляем пользователя о модерации
    await message.answer("⏳ Ваш пост отправлен на модерацию. Ожидайте решения администратора.")
    
    # Пересылаем пост всем активным администраторам
    sent_messages = []
    for admin_id in ADMIN_IDS:
        if not await storage.is_admin_on_vacation(admin_id):
            try:
                # Копируем сообщение с кнопками модерации
                if message.content_type == 'text':
                    sent_msg = await bot.send_message(
                        admin_id,
                        f"📨 Новый пост от пользователя @{message.from_user.username or message.from_user.id}:\n\n{message.text}",
                        reply_markup=create_admin_keyboard(0)  # Временный ID
                    )
                else:
                    caption = f"📨 Новый пост от пользователя @{message.from_user.username or message.from_user.id}"
                    if message.caption:
                        caption += f"\n\n{message.caption}"
                    
                    if message.content_type == 'photo':
                        sent_msg = await bot.send_photo(
                            admin_id,
                            message.photo[-1].file_id,
                            caption=caption,
                            reply_markup=create_admin_keyboard(0)
                        )
                    elif message.content_type == 'video':
                        sent_msg = await bot.send_video(
                            admin_id,
                            message.video.file_id,
                            caption=caption,
                            reply_markup=create_admin_keyboard(0)
                        )
                    elif message.content_type == 'document':
                        sent_msg = await bot.send_document(
                            admin_id,
                            message.document.file_id,
                            caption=caption,
                            reply_markup=create_admin_keyboard(0)
                        )
                
                sent_messages.append(sent_msg)
            except Exception as e:
                logger.error(f"Ошибка отправки администратору {admin_id}: {e}")
    
    if sent_messages:
        # Сохраняем первый отправленный пост как основной для модерации
        await storage.add_pending_post(message, sent_messages[0])
        
        # Обновляем кнопки с правильным ID сообщения
        for sent_msg in sent_messages:
            await bot.edit_message_reply_markup(
                chat_id=sent_msg.chat.id,
                message_id=sent_msg.message_id,
                reply_markup=create_admin_keyboard(sent_msg.message_id)
            )

@dp.callback_query(F.data.startswith("approve_"))
async def approve_post(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен.")
        return
        
    post_id = int(callback.data.split("_")[1])
    post_data = await storage.get_pending_post(post_id)
    
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан.")
        return
    
    try:
        # Публикуем в канал
        if post_data['content'].content_type == 'text':
            await bot.send_message(
                CHANNEL_ID,
                post_data['content'].text
            )
        else:
            caption = post_data['content'].caption
            if post_data['content'].content_type == 'photo':
                await bot.send_photo(
                    CHANNEL_ID,
                    post_data['content'].photo[-1].file_id,
                    caption=caption
                )
            elif post_data['content'].content_type == 'video':
                await bot.send_video(
                    CHANNEL_ID,
                    post_data['content'].video.file_id,
                    caption=caption
                )
            elif post_data['content'].content_type == 'document':
                await bot.send_document(
                    CHANNEL_ID,
                    post_data['content'].document.file_id,
                    caption=caption
                )
        
        # Уведомляем пользователя
        await bot.send_message(
            post_data['user_id'],
            "✅ Ваш пост был одобрен и опубликован в канале!"
        )
        
        # Удаляем сообщение у администратора
        await bot.delete_message(
            callback.message.chat.id,
            callback.message.message_id
        )
        
        await storage.remove_pending_post(post_id)
        await callback.answer("✅ Пост опубликован!")
        
    except Exception as e:
        logger.error(f"Ошибка публикации поста: {e}")
        await callback.answer("❌ Ошибка при публикации поста.")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_post(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен.")
        return
        
    post_id = int(callback.data.split("_")[1])
    post_data = await storage.get_pending_post(post_id)
    
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан.")
        return
    
    try:
        # Уведомляем пользователя
        await bot.send_message(
            post_data['user_id'],
            "❌ Ваш пост был отклонен администратором."
        )
        
        # Удаляем сообщение у администратора
        await bot.delete_message(
            callback.message.chat.id,
            callback.message.message_id
        )
        
        await storage.remove_pending_post(post_id)
        await callback.answer("❌ Пост отклонен!")
        
    except Exception as e:
        logger.error(f"Ошибка отклонения поста: {e}")
        await callback.answer("❌ Ошибка при отклонении поста.")

@dp.callback_query(F.data == "vacation_on")
async def vacation_on(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен.")
        return
    
    available_admins = await storage.get_available_admins_count()
    if available_admins <= 1:
        await callback.answer("❌ Вы не можете уйти в отпуск, так как вы последний активный администратор.")
        return
    
    await storage.set_admin_vacation(callback.from_user.id, True)
    await callback.message.edit_text("✅ Вы ушли в отпуск. Новые посты не будут вам приходить.")
    await callback.answer()

@dp.callback_query(F.data == "vacation_off")
async def vacation_off(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен.")
        return
    
    await storage.set_admin_vacation(callback.from_user.id, False)
    await callback.message.edit_text("✅ Вы вернулись из отпуска. Теперь вы будете получать новые посты.")
    await callback.answer()

async def main():
    # Инициализация статусов отпусков
    for admin_id in ADMIN_IDS:
        await storage.set_admin_vacation(admin_id, False)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
