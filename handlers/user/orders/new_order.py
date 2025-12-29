from aiogram import types, F, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.utils import connection
from fsm.user.order import PlaceOrderFSM, DeliveryOrderFSM, SoberDriverFSM
from markups.user.order import order_type_markup


async def send_order_types(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer(
        "Выберите тип заказа",
        reply_markup=order_type_markup
    )

    await c.answer()


async def start_city_order(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(PlaceOrderFSM.settlement_state)
    await c.message.answer(
        "Укажите название населенного пункта"
    )

    await c.answer()


async def handle_city_settlement(m: types.Message, state: FSMContext):
    await state.set_state(PlaceOrderFSM.description_state)
    await state.update_data(settlement=m.text.strip())

    await m.answer(
        "Введите описание заказа"
    )


@connection
async def handle_city_description(m: types.Message, state: FSMContext, db_session: AsyncSession):
    await state.update_data(description=m.text.strip())
    s_data = await state.get_data()
    await state.clear()

    await m.answer(
        "Заказ успешно опубликован!"
    )


async def start_deliver_order(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(DeliveryOrderFSM.settlement_state)

    await c.message.answer(
        "Введите населенный пункт доставки"
    )

    await c.answer()


async def handle_delivery_settlement(m: types.Message, state: FSMContext):
    await state.set_state(DeliveryOrderFSM.description_state)
    await state.update_data(settlement=m.text)

    await m.answer(
        "Введите подробное описание заказа"
    )


@connection
async def handle_delivery_description(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.update_data(description=m.text.strip())
    s_data = await state.get_data()
    await state.clear()

    await m.answer(
        "Заказ успешно опубликован!"
    )


async def start_sober_driver_order(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(SoberDriverFSM.from_state)

    await c.message.answer(
        "Укажите точку начала пути"
    )

    await c.answer()


async def handle_from(m: types.Message, state: FSMContext):
    await state.set_state(SoberDriverFSM.dest_state)
    await state.update_data(start_point=m.text)

    await m.answer(
        "Теперь укажите конечную точку пути"
    )


async def handle_destination(m: types.Message, state: FSMContext):
    await state.set_state(SoberDriverFSM.description_state)
    await state.update_data(end_point=m.text)

    await m.answer(
        "Введите подробное описание заказа"
    )


@connection
async def handle_sdriver_description(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.update_data(description=m.text.strip())
    s_data = await state.get_data()
    await state.clear()

    await m.answer(
        "Заказ успешно опубликован!"
    )


def register_orders_handlers(dp: Dispatcher):
    dp.callback_query.register(send_order_types, F.data == "new_order")

    dp.callback_query.register(start_city_order, F.data == "ordertype_2")
    dp.message.register(handle_city_settlement, StateFilter(PlaceOrderFSM.settlement_state))
    dp.message.register(handle_city_description, StateFilter(PlaceOrderFSM.description_state))

    dp.callback_query.register(start_deliver_order, F.data == "ordertype_3")
    dp.message.register(handle_delivery_settlement, StateFilter(DeliveryOrderFSM.settlement_state))
    dp.message.register(handle_delivery_description, StateFilter(DeliveryOrderFSM.description_state))

    dp.callback_query.register(start_sober_driver_order, F.data == "ordertype_4")
    dp.message.register(handle_from, StateFilter(SoberDriverFSM.from_state))
    dp.message.register(handle_destination, StateFilter(SoberDriverFSM.dest_state))
    dp.message.register(handle_sdriver_description, StateFilter(SoberDriverFSM.description_state))

