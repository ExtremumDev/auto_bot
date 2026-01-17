from aiogram import types, F, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import OrderDAO, UserDAO
from database.utils import connection
from fsm.user.order import PlaceOrderFSM, DeliveryOrderFSM, SoberDriverFSM
from markups.user.order import order_type_markup
from utils.enums import OrderType


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
    await state.set_state(PlaceOrderFSM.price_state)
    await state.update_data(settlement=m.text.strip())

    await m.answer(
        "Введите цену за заказ"
    )


async def handle_city_price(m: types.Message, state: FSMContext):
    try:
        price = int(m.text)
        await state.set_state(PlaceOrderFSM.date_state)
        await state.update_data(price=price)

        await m.answer(
            "Введите дату заказа"
        )
    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )


async def handle_city_date(m: types.Message, state: FSMContext):
    await state.set_state(PlaceOrderFSM.description_state)
    await state.update_data(date=m.text)

    await m.answer(
        "Введите описание заказа"
    )



@connection
async def handle_city_description(m: types.Message, state: FSMContext, db_session: AsyncSession):
    await state.update_data(description=m.text.strip())
    s_data = await state.get_data()
    await state.clear()

    user = await UserDAO.get_obj(session=db_session, telegram_id=m.from_user.id)

    order = await OrderDAO.add_order(
        creator_id=user.id,
        price=s_data["price"],
        date=s_data["date"],
        session=db_session,
        order_type=OrderType.CITY,
        settlement=s_data['settlement'],
        description=s_data['description']
    )

    await m.answer(
        "Заказ успешно опубликован!"
    )


async def start_deliver_order(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(DeliveryOrderFSM.settlement_state)

    await c.message.answer(
        "Введите населенный пункт доставки. Или укажите точку А и точку Б"
    )

    await c.answer()


async def handle_delivery_settlement(m: types.Message, state: FSMContext):
    await state.set_state(DeliveryOrderFSM.price_state)
    await state.update_data(settlement=m.text)

    await m.answer(
        "Введите цену за заказ"
    )


async def handle_delivery_price(m: types.Message, state: FSMContext):
    try:
        price = int(m.text)
        await state.set_state(DeliveryOrderFSM.date_state)
        await state.update_data(price=price)
        await m.answer("Введите дату заказа")
    except ValueError:
        await m.answer(
            "Необходимо ввести число, попробуйте еще раз"
        )


async def handle_delivery_date(m: types.Message, state: FSMContext):
    await state.set_state(DeliveryOrderFSM.description_state)
    await state.update_data(date=m.text)

    await m.answer(
        "Введите подробное описание заказа"
    )


@connection
async def handle_delivery_description(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.update_data(description=m.text.strip())
    s_data = await state.get_data()
    await state.clear()

    user = await UserDAO.get_obj(session=db_session, telegram_id=m.from_user.id)

    order = await OrderDAO.add_order(
        creator_id=user.id,
        session=db_session,
        price=s_data["price"],
        date=s_data["date"],
        order_type=OrderType.DELIVERY,
        settlement=s_data['settlement'],
        description=s_data['description']
    )

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
    await state.set_state(SoberDriverFSM.price_state)
    await state.update_data(end_point=m.text)

    await m.answer(
        "Веедите цену за заказ"
    )


async def handle_sdriver_price(m: types.Message, state: FSMContext):
    try:
        price = int(m.text)
        await state.set_state(SoberDriverFSM.date_state)
        await state.update_data(price=price)

        await m.answer(
            "Введите датузаказа"
        )
    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )


async def handle_sdriver_date(m: types.Message, state: FSMContext):
    await state.set_state(SoberDriverFSM.description_state)
    await state.update_data(date=m.text)

    await m.answer(
        "Введите подробное описание заказа"
    )


@connection
async def handle_sdriver_description(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.update_data(description=m.text.strip())
    s_data = await state.get_data()
    await state.clear()

    user = await UserDAO.get_obj(session=db_session, telegram_id=m.from_user.id)

    order = await OrderDAO.add_order(
        price=s_data["price"],
        date=s_data["date"],
        creator_id=user.id,
        session=db_session,
        order_type=OrderType.SOBER_DRIVER,
        from_point=s_data['start_point'],
        destination_point=s_data['end_point'],
        description=s_data['description']
    )

    await m.answer(
        "Заказ успешно опубликован!"
    )


def register_orders_handlers(dp: Dispatcher):
    dp.callback_query.register(send_order_types, F.data == "new_order")

    dp.callback_query.register(start_city_order, F.data == "ordertype_2")
    dp.message.register(handle_city_settlement, StateFilter(PlaceOrderFSM.settlement_state))
    dp.message.register(handle_city_price, StateFilter(PlaceOrderFSM.price_state))
    dp.message.register(handle_city_date, StateFilter(PlaceOrderFSM.date_state))
    dp.message.register(handle_city_description, StateFilter(PlaceOrderFSM.description_state))

    dp.callback_query.register(start_deliver_order, F.data == "ordertype_3")
    dp.message.register(handle_delivery_settlement, StateFilter(DeliveryOrderFSM.settlement_state))
    dp.message.register(handle_delivery_price, StateFilter(DeliveryOrderFSM.price_state))
    dp.message.register(handle_delivery_date, StateFilter(DeliveryOrderFSM.date_state))
    dp.message.register(handle_delivery_description, StateFilter(DeliveryOrderFSM.description_state))

    dp.callback_query.register(start_sober_driver_order, F.data == "ordertype_4")
    dp.message.register(handle_from, StateFilter(SoberDriverFSM.from_state))
    dp.message.register(handle_destination, StateFilter(SoberDriverFSM.dest_state))
    dp.message.register(handle_sdriver_price, StateFilter(SoberDriverFSM.price_state))
    dp.message.register(handle_sdriver_date, StateFilter(SoberDriverFSM.date_state))
    dp.message.register(handle_sdriver_description, StateFilter(SoberDriverFSM.description_state))

