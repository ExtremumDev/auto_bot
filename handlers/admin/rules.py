import asyncio

from aiogram import types, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import RulesData
from filters.users import AdminFilter
from fsm.admin.admin import EditRulesFSM
from markups.admin.main import return_to_admin_panel_markup


async def ask_new_rules(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer(
        "Текущие правила выглядят так👇"
    )
    await asyncio.sleep(0.5)
    await c.message.answer(
        RulesData.rules
    )

    await state.set_state(EditRulesFSM.rules_text_state)
    await c.message.answer(
        "Пришлите новый текст для правил",
        reply_markup=return_to_admin_panel_markup
    )


async def handle_new_rules_text(m: types.Message, state: FSMContext):
    await state.clear()
    RulesData.rules = m.text

    await m.answer(
        "Правила были успешно изменены!"
    )


def register_edit_rules_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_new_rules, F.data == "edit_rules", AdminFilter())
    dp.message.register(handle_new_rules_text, StateFilter(EditRulesFSM.rules_text_state))
