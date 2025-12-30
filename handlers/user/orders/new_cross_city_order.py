from aiogram import types, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import OrderDAO
from database.utils import connection
from fsm.user.order import CrossCityOrderFSM
from markups.user.order import order_speed_markup
from utils.enums import OrderType, CarClass


async def start_order(c: types.CallbackQuery, state: FSMContext):
    order_type_number = int(c.data.split('_')[1])

    order_type = OrderType(order_type_number)

    match order_type:
        case OrderType.CROSS_CITY:
            await state.set_state(CrossCityOrderFSM.from_city_state)

            await c.message.answer(
                "Укажите точку начала пути(город)"
            )

    await c.answer()

async def handle_from_city(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.from_add_state)
    await state.update_data(from_city=m.text.strip())

    await m.answer(
        "Добавьте комментарий про точку начала(адрес, координаты и т.д.)"
    )


async def handle_from_additional(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.dest_city_state)
    await state.update_data(from_add=m.text.strip())

    await m.answer(
        "Укажите пункт назначения(город)"
    )

async def handle_dest_city(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.dest_add_state)
    await state.update_data(dest_city=m.text.strip())

    await m.answer(
        "Добавьте комментарий про точку назначения(адрес, координаты и т.д.)"
    )


async def handle_dest_additional(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.intermediate_points_state)
    await state.update_data(dest_add=m.text.strip())

    await m.answer(
        "Укажите дополнительные промежуточные точки маршрута(необязательно)"
    )


async def handle_intermediate_points(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.speed_state)
    await state.update_data(intermediate_points=m.text.strip())

    await m.answer(
        "Выберите тип заказа",
        reply_markup=order_speed_markup
    )


async def handle_order_speed(c: types.CallbackQuery, state: FSMContext):
    order_speed = int(c.data.split('_')[1])
    await state.update_data(order_speed=order_speed)

    if order_speed == 2:
        await state.set_state(CrossCityOrderFSM.date_state)
        await c.message.answer(
            "Укажите дату поездки"
        )
    else:
        await state.set_state(CrossCityOrderFSM.time_state)

        await c.message.answer(
            "Укажите время поездки"
        )


async def handle_date(m: types.Message, state: FSMContext):
    date = m.text # verification

    await state.set_state(CrossCityOrderFSM.time_state)
    await state.update_data(date=date)

    await m.answer(
        "Укажите вермя поездки"
    )


async def handle_time(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.passengers_state)
    await state.update_data(time=m.text.strip())

    await m.answer(
        "Введите количество пассажиров"
    )


async def handle_passengers_count(m: types.Message, state: FSMContext):
    try:
        passengers_count = int(m.text)

        await state.set_state(CrossCityOrderFSM.car_class_state)
        await state.update_data(passengers_count=passengers_count)

        await  m.answer(
            "Выберите необходимый класс автомобиля",
            reply_markup=CarClass.get_choice_by_passengers_number(passengers_count)
        )

    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )


@connection
async def handle_car_class(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    car_class_id = c.data.split('_')[1]
    await state.update_data(car_class=CarClass(car_class_id))

    s_data = await state.get_data()
    await state.clear()

    order = await OrderDAO.add_order(
        session=db_session,
        order_type=OrderType.CROSS_CITY,
        from_city=s_data["from_city"],
        from_add=s_data["from_add"],
        destionation_city=s_data["dest_city"],
        destination_add=s_data["dest_add"],
        intermediate_points=s_data["intermediate_points"],
        speed=s_data['order_speed'],
        date=s_data.get("date", None),
        time=s_data['time'],
        passenger_number=s_data['passenger_count'],
        car_class=s_data['car_class'],
    )

    await c.message.answer(
        "Заказ успешно опубликован!"
    )

    await c.answer()



def register_new_cross_city_order_handlers(dp: Dispatcher):

    dp.callback_query.register(start_order, F.data == "ordertype_1")
    dp.message.register(handle_from_city, StateFilter(CrossCityOrderFSM.from_city_state))
    dp.message.register(handle_from_additional, StateFilter(CrossCityOrderFSM.from_add_state))
    dp.message.register(handle_dest_city, StateFilter(CrossCityOrderFSM.dest_city_state))
    dp.message.register(handle_dest_additional, StateFilter(CrossCityOrderFSM.dest_add_state))
    dp.message.register(handle_intermediate_points, StateFilter(CrossCityOrderFSM.intermediate_points_state))
    dp.callback_query.register(
        handle_order_speed,
        F.data.startswith("orderspeed_"),
        StateFilter(CrossCityOrderFSM.speed_state)
    )
    dp.message.register(handle_date, StateFilter(CrossCityOrderFSM.date_state))
    dp.message.register(handle_time, StateFilter(CrossCityOrderFSM.time_state))
    dp.message.register(handle_passengers_count, StateFilter(CrossCityOrderFSM.passengers_state))
    dp.callback_query.register(
        handle_car_class,
        F.data.startswith("carclass_"),
        StateFilter(CrossCityOrderFSM.car_class_state)
    )

