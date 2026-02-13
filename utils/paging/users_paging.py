import math

from aiogram import types
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import UserDAO
from .base_paging import Paging


class UsersPaging(Paging):
    def __init__(self, page: int = 0):
        super().__init__(page, prefix='um')


    async def get_queryset(self, db_session: AsyncSession, *args, **kwargs):
        self.queryset = await UserDAO.get_many(db_session)
        self.total_pages = math.ceil(len(self.queryset) / self.objects_in_page)


    def get_reply_markup(
        self,
        reply_markup: types.InlineKeyboardMarkup = None,
        extra_data: str ='',
        *args, **kwargs
    ):
        users_list_markup = types.InlineKeyboardMarkup(
            inline_keyboard=[]
        )

        users_list_markup.inline_keyboard.append(
            [InlineKeyboardButton(text="🔍 Поиск по имени пользователя", callback_data="search_users")]
        )

        for u in self.queryset:
            users_list_markup.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=u.telegram_username if u.telegram_username else str(u.telegram_id) + " 🚫 " if u.is_blocked else " 🟢 ",
                        callback_data=f"usermanage_{u.id}"
                    )
                ]
            )

        return super().get_reply_markup(reply_markup=users_list_markup)
