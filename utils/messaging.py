from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputFile, InlineKeyboardMarkup

from bot import bot
from config import AdminsSettings
from utils.logger import get_bot_logger


async def send_message_to_admins(message: str, reply_markup: InlineKeyboardMarkup = None, photo: InputFile = None):
    for admin_id in set(AdminsSettings.ADMIN_ID + AdminsSettings.MAIN_ADMIN_ID):
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
                reply_markup=reply_markup
            )
        except TelegramBadRequest:
            get_bot_logger().error(f"Failed to send message to admin with id {admin_id}")
