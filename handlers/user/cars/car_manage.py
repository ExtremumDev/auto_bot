from aiogram import types, Dispatcher, F

from markups.user.car_manage import get_car_manage_menu_markup


async def send_car_manage_menu(c: types.CallbackQuery):
    await c.message.answer(
        "Управление автомобилями",
        reply_markup=get_car_manage_menu_markup()
    )
    await c.answer()


def register_car_manage_handlers(dp: Dispatcher):
    dp.callback_query.register(send_car_manage_menu, F.data == "car_manage")
