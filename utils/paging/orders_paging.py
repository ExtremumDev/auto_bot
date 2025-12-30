import math

from aiogram import types
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import OrderDAO
from .base_paging import Paging


class OrdersPaging(Paging):
    def __init__(self, page: int = 0):
        super().__init__(page, prefix='o')


    async def get_queryset(self, db_session: AsyncSession, *args, **kwargs):
        self.queryset = await OrderDAO.get_active_orders(session=db_session)
        self.total_pages = math.ceil(len(self.queryset) / self.objects_in_page)


    def get_reply_markup(
        self,
        reply_markup: types.InlineKeyboardMarkup = None,
        extra_data: str ='',
        *args, **kwargs
    ):
        orders_list_markup = types.InlineKeyboardMarkup(
            inline_keyboard=[]
        )

        for o in self.queryset:
            orders_list_markup.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=o.get_order_name(),
                        callback_data=f"order_{o.id}"
                    )
                ]
            )

        return super().get_reply_markup(reply_markup=orders_list_markup)
