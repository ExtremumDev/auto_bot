from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from database.dao import OrderDAO, UserDAO
from database.utils import connection
from fsm.user.order import CrossCityOrderFSM
from handlers.user.orders.new_order import post_order
from markups.user.order import order_speed_markup, get_manage_order_markup
from utils.enums import OrderType, CarClass
from utils.utils import check_user_blocked


@connection
async def start_order(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession):
    user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

    if user and (user.is_blocked or (not user.driver) or (not user.driver.is_moderated)):
        await c.answer("Вы не имеете права публикоавть заказы")
        return
    order_type_number = int(c.data.split('_')[1])

    order_type = OrderType(order_type_number)

    match order_type:
        case OrderType.CROSS_CITY:
            await state.set_state(CrossCityOrderFSM.from_state)

            message = await c.message.answer(
                "Укажите название населённого пункта начала пути и по возможности, район(улицу, координаты)"
            )

            await state.update_data(prev_message=message.message_id)


    await c.answer()


async def handle_from(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.destination_state)
    await state.update_data(from_city=m.text.strip())

    message = await m.answer(
        "Укажите название населённого пункта назначения и по возможности, район(улицу, координаты)"
    )

    await state.update_data(prev_message=message.message_id)

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass


async def handle_destination(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.intermediate_points_state)
    await state.update_data(dest_city=m.text.strip())

    message = await m.answer(
        "Укажите дополнительные промежуточные точки маршрута или напишите \"Нет\""
    )

    await state.update_data(prev_message=message.message_id)

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass


async def handle_intermediate_points(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.speed_state)
    await state.update_data(intermediate_points=m.text.strip())

    message = await m.answer(
        "Выберите тип заказа",
        reply_markup=order_speed_markup
    )

    await state.update_data(prev_message=message.message_id)

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass


async def handle_order_speed(c: types.CallbackQuery, state: FSMContext):
    order_speed = int(c.data.split('_')[1])
    await state.update_data(order_speed=order_speed)

    if order_speed == 2:
        await state.set_state(CrossCityOrderFSM.date_state)
        message = await c.message.answer(
            "Укажите дату начала поездки"
        )
    else:
        await state.set_state(CrossCityOrderFSM.time_state)

        message = await c.message.answer(
            "Укажите время начала поездки"
        )

    await state.update_data(prev_message=message.message_id)

    try:
        await c.bot.delete_message(chat_id=c.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass


async def handle_date(m: types.Message, state: FSMContext):
    date = m.text # verification

    await state.set_state(CrossCityOrderFSM.time_state)
    await state.update_data(date=date)

    message = await m.answer(
        "Укажите время начала поездки"
    )

    await state.update_data(prev_message=message.message_id)

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass


async def handle_time(m: types.Message, state: FSMContext):
    await state.set_state(CrossCityOrderFSM.passengers_state)
    await state.update_data(time=m.text.strip())

    message = await m.answer(
        "Введите количество пассажиров"
    )

    await state.update_data(prev_message=message.message_id)

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass


async def handle_passengers_count(m: types.Message, state: FSMContext):
    try:
        passengers_count = int(m.text)

        await state.set_state(CrossCityOrderFSM.car_class_state)
        await state.update_data(passengers_count=passengers_count)

        message = await  m.answer(
            "Выберите необходимый класс автомобиля",
            reply_markup=CarClass.get_choice_by_passengers_number(passengers_count)
        )

        await state.update_data(prev_message=message.message_id)

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )


async def handle_car_class(c: types.CallbackQuery, state: FSMContext):
    car_class_id = c.data.split('_')[1]

    await state.set_state(CrossCityOrderFSM.nt_distance_state)
    await state.update_data(car_class=CarClass(car_class_id))

    message = await c.message.answer(
        "Введите километраж по НТ(новые территории), если нет - 0"
    )

    await state.update_data(prev_message=message.message_id)

    await c.answer()
    try:
        await c.bot.delete_message(chat_id=c.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass



async def handle_new_territory_distance(m: types.Message, state: FSMContext):
    try:
        distance = int(m.text)
        await state.update_data(nt_distance=distance)

        await state.set_state(CrossCityOrderFSM.rf_distance_state)
        message = await m.answer(
            "Укажите километраж по РФ, если нет - введите 0"
        )

        await state.update_data(prev_message=message.message_id)

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )

async def handle_rf_distance(m: types.Message, state: FSMContext):
    try:
        distance = int(m.text)
        await state.update_data(rf_distance=distance)

        await state.set_state(CrossCityOrderFSM.price_state)

        message = await m.answer(
            "Введите цену за поездку водителю на руки без учёта стоимости платных дорог"
        )

        await state.update_data(prev_message=message.message_id)

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )



async def handle_price(m: types.Message, state: FSMContext):
    try:
        price = m.text
        await state.update_data(price=price)

        await state.set_state(CrossCityOrderFSM.description_state)
        message = await m.answer(
            "Введите свободный комментарий о поездке или напишите \"Нет\""
        )

        await state.update_data(prev_message=message.message_id)

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )



@connection
async def handle_description(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.update_data(description=m.text[:99])

    s_data = await state.get_data()
    await state.clear()

    user = await UserDAO.get_obj(session=db_session, telegram_id=m.from_user.id)

    order = await OrderDAO.add_order(
        creator_id=user.id,
        session=db_session,
        order_type=OrderType.CROSS_CITY,
        from_city=s_data["from_city"],
        destination_city=s_data["dest_city"],
        intermediate_points=s_data["intermediate_points"],
        speed=s_data['order_speed'],
        date=s_data.get("date", None),
        time=s_data['time'],
        passengers_number=s_data['passengers_count'],
        car_class=s_data['car_class'],
        new_territory_distance=s_data["nt_distance"],
        rf_distance=s_data["rf_distance"],
        price=s_data["price"],
        description=s_data["description"]
    )

    await m.answer(
        "Заказ успешно опубликован!"
    )
    await m.answer(
        text=order.get_description(),
        reply_markup=get_manage_order_markup(order.id)
    )

    if order.creator.telegram_username != m.from_user.username:
        order.creator.telegram_username = m.from_user.username
        await db_session.commit()

    await post_order(m.bot, order=order, db_session=db_session)


    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass



def register_new_cross_city_order_handlers(dp: Dispatcher):

    dp.callback_query.register(start_order, F.data == "ordertype_1")
    dp.message.register(handle_from, StateFilter(CrossCityOrderFSM.from_state))
    dp.message.register(handle_destination, StateFilter(CrossCityOrderFSM.destination_state))
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

    dp.message.register(handle_new_territory_distance, StateFilter(CrossCityOrderFSM.nt_distance_state))
    dp.message.register(handle_rf_distance, StateFilter(CrossCityOrderFSM.rf_distance_state))
    dp.message.register(handle_price, StateFilter(CrossCityOrderFSM.price_state))
    dp.message.register(handle_description, StateFilter(CrossCityOrderFSM.description_state))

