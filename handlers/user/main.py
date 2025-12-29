from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext

from config import RulesData
from markups.user.main import get_main_markup
from utils.text import main_menu_message


async def to_main_menu(c: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await c.message.answer(
        main_menu_message,
        reply_markup=get_main_markup(c.from_user.id)
    )

    await c.answer()


async def send_rules(c: types.CallbackQuery):
    await c.message.answer(
        RulesData.rules
    )
    await c.answer()


def register_main_handlers(dp: Dispatcher):
    dp.callback_query.register(to_main_menu, F.data == "main_menu")
    dp.callback_query.register(send_rules, F.data == "rules")
