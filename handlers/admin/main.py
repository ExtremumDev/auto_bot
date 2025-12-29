from aiogram import types, Dispatcher, F

from markups.admin.main import admin_panel_markup


async def open_admin_panel(c: types.CallbackQuery):
    await c.message.answer(
        "Открыта панель администратора",
        reply_markup=admin_panel_markup
    )

    await c.answer()


def register_main_admin_handlers(dp: Dispatcher):
    dp.callback_query.register(open_admin_panel, F.data == "admin_panel")
