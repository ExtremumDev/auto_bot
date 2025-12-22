from aiogram import types, Dispatcher
from aiogram.filters import StateFilter


async def answer_callback_query(c: types.CallbackQuery):
    await c.answer()


def register_extra_handlers(dp: Dispatcher):
    dp.callback_query.register(answer_callback_query, StateFilter('*'))
