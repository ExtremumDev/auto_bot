from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from config import RulesData
from markups.user.main import get_main_markup
from utils.text import main_menu_message


async def to_main_menu_callback(c: types.CallbackQuery, state: FSMContext):

    await to_main_menu(c.message, state)

    await c.answer()


async def to_main_menu(m: types.Message, state: FSMContext):
    await state.clear()

    await m.answer(
        main_menu_message,
        reply_markup=get_main_markup(m.from_user.id)
    )

    try:
        await m.delete()
    except TelegramBadRequest:
        pass


async def send_rules(c: types.CallbackQuery):
    await c.message.answer(
        RulesData.rules
    )
    await c.answer()


async def cancel_action(c: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await c.answer("Дейсвтие отменено")


def register_main_handlers(dp: Dispatcher):
    dp.callback_query.register(to_main_menu_callback, F.data == "main_menu", StateFilter('*'))
    dp.message.register(to_main_menu, Command("menu"), StateFilter('*'))
    dp.callback_query.register(send_rules, F.data == "rules")
    dp.callback_query.register(cancel_action, F.data == "cancel_action")
