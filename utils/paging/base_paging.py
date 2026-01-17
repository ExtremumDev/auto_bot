from aiogram import types, F
from sqlalchemy.ext.asyncio import AsyncSession

from database.utils import connection


class Paging:
    EMPTY_SET_MESSAGE = "Не найдено объектов"
    prefix = ""
    total_pages = 0
    queryset = []
    objects_in_page = 5

    def __init__(self, page: int = 0, prefix: str = ''):
        self.page = page
        self.is_prev = False
        self.is_next = False
        self.prefix = prefix


    async def get_queryset(self, db_session: AsyncSession, *args, **kwargs):
        pass

    def get_paging_kb(self, extra_data: str =''):
        inline_keyboard = []
        paging = []
        if self.is_prev:
            paging.append(
                types.InlineKeyboardButton(
                    text='<-',
                    callback_data=f"{self.prefix}prev_{self.page}{extra_data}"
                )
            )
        if self.is_next:
            paging.append(
                types.InlineKeyboardButton(
                    text='->',
                    callback_data=f"{self.prefix}next_{self.page}{extra_data}"
                )
            )

        if paging:
            inline_keyboard.append(paging)
            inline_keyboard.append(
                [
                    types.InlineKeyboardButton(
                        text=f"Страница {self.page + 1} из {self.total_pages}",
                        callback_data=' '
                    )
                ]
            )
        return inline_keyboard

    def get_reply_markup(
        self,
        reply_markup: types.InlineKeyboardMarkup = None,
        extra_data: str ='',
        *args, **kwargs
    ):
        reply_markup.inline_keyboard.extend(self.get_paging_kb(extra_data))

        if not reply_markup.inline_keyboard:
            reply_markup.inline_keyboard.extend(
                [
                    [
                        types.InlineKeyboardButton(
                            text=self.EMPTY_SET_MESSAGE,
                            callback_data=' '
                        )
                    ]
                ]
            )
        return reply_markup

    async def get_current_page(self):
        if self.queryset:
            if self.page > 0:
                self.is_prev = True
            diff = len(self.queryset) - self.page * self.objects_in_page
            if diff > 0:
                self.queryset = self.queryset[self.page * self.objects_in_page: (self.page + 1) * self.objects_in_page]
                if diff > self.objects_in_page:
                    self.is_next = True
            else:
                self.queryset = []

    async def create_next_page(self):
        if self.queryset:
            self.is_prev = True
            self.page += 1
            diff = len(self.queryset) - self.page * self.objects_in_page
            if diff > 0:
                if diff > self.objects_in_page:
                    self.is_next = True

                self.queryset = self.queryset[self.page * self.objects_in_page: (self.page + 1) * self.objects_in_page]

            else:
                self.queryset = []

    async def create_prev_page(self):
        if self.queryset:
            self.page -= 1
            if self.page > 0:
                self.is_prev = True
            if self.page >= 0:

                diff = len(self.queryset) - self.page * self.objects_in_page
                if diff > 0:
                    if diff > self.objects_in_page:
                        self.is_next = True

                    self.queryset = self.queryset[self.page * self.objects_in_page: (self.page + 1) * self.objects_in_page]

                else:
                    self.queryset = []

    @classmethod
    @connection
    async def next_page_handler(cls, c: types.CallbackQuery, db_session: AsyncSession, *args):
        c_data = c.data.split('_')

        page = int(c_data[1])

        paging = cls(page)
        await paging.get_queryset(db_session=db_session)
        await paging.create_next_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup()
        )

    @classmethod
    @connection
    async def prev_page_handler(cls, c: types.CallbackQuery, db_session: AsyncSession, *args):
        c_data = c.data.split('_')

        page = int(c_data[1])

        paging = cls(page)
        await paging.get_queryset(db_session=db_session)
        await paging.create_prev_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup()
        )

    @classmethod
    def register_paging_handlers(cls, dp, prefix=''):
        dp.callback_query.register(cls.prev_page_handler, F.data.startswith(prefix + 'prev_'))
        dp.callback_query.register(cls.next_page_handler, F.data.startswith(prefix + 'next_'))