
from aiogram import types, F, Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import OrderDAO, UserDAO
from database.utils import connection
from fsm.user.order import PlaceOrderFSM, DeliveryOrderFSM, SoberDriverFSM, FreeOrderFSM
from handlers.admin.users_manage import ask_confirm_administrator
from markups.user.order import order_type_markup, get_accept_order_markup, get_manage_order_markup
from utils.enums import OrderType
from utils.utils import check_user_blocked


async def send_order_types(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer(
        "Выберите тип заказа",
        reply_markup=order_type_markup
    )

    await c.answer()

    try:
        await c.message.delete()
    except TelegramBadRequest:
        pass


@connection
async def start_city_order(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession):
    user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

    if user and (user.is_blocked or (not user.driver) or (not user.driver.is_moderated)):
        await c.answer("Вы не имеете права публикоавть заказы")
        return

    await state.set_state(PlaceOrderFSM.settlement_state)
    message = await c.message.answer(
        "Укажите название населенного пункта"
    )

    await c.answer()

    await state.update_data(prev_message=message.message_id)

    try:
        await c.message.delete()
    except TelegramBadRequest:
        pass


async def handle_city_settlement(m: types.Message, state: FSMContext):
    await state.set_state(PlaceOrderFSM.price_state)
    await state.update_data(settlement=m.text.strip())

    message = await m.answer(
        "Введите цену за заказ"
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)


async def handle_city_price(m: types.Message, state: FSMContext):
    try:
        price = m.text
        await state.set_state(PlaceOrderFSM.date_state)
        await state.update_data(price=price)

        message = await m.answer(
            "Введите дату и время заказа"
        )

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

        await state.update_data(prev_message=message.message_id)
    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )


async def handle_city_date(m: types.Message, state: FSMContext):
    await state.set_state(PlaceOrderFSM.description_state)
    await state.update_data(date=m.text)

    message = await m.answer(
        "Укажите детали заказа или напишите \"Нет\""
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)



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

    if order.creator.telegram_username != m.from_user.username:
        order.creator.telegram_username = m.from_user.username
        await db_session.commit()
    if m.from_user.username is None:
        await m.answer(
            "❗️ Вы не указали имя пользвотеля в телеграмме, связь с другими пользователями бота будет невозможна"
        )

    await post_order(bot=m.bot, order=order, db_session=db_session)

    await m.answer(
        "Заказ успешно опубликован!"
    )
    await m.answer(
        text=order.get_description(),
        reply_markup=get_manage_order_markup(order.id)
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=s_data['prev_message'])
    except TelegramBadRequest:
        pass


@connection
async def start_deliver_order(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession):
    user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

    if user and (user.is_blocked or (not user.driver) or (not user.driver.is_moderated)):
        await c.answer("Вы не имеете права публикоавть заказы")
        return
    await state.set_state(DeliveryOrderFSM.settlement_state)

    message = await c.message.answer(
        "Введите населенный пункт доставки. Или укажите точку А и точку Б"
    )

    await state.update_data(prev_message=message.message_id)

    await c.answer()

    try:
        await c.message.delete()
    except TelegramBadRequest:
        pass


async def handle_delivery_settlement(m: types.Message, state: FSMContext):
    await state.set_state(DeliveryOrderFSM.price_state)
    await state.update_data(settlement=m.text)

    message = await m.answer(
        "Введите цену за заказ"
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)


async def handle_delivery_price(m: types.Message, state: FSMContext):
    try:
        price = m.text
        await state.set_state(DeliveryOrderFSM.date_state)
        await state.update_data(price=price)
        message = await m.answer("Введите дату и время заказа")

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

        await state.update_data(prev_message=message.message_id)
    except ValueError:
        await m.answer(
            "Необходимо ввести число, попробуйте еще раз"
        )


async def handle_delivery_date(m: types.Message, state: FSMContext):
    await state.set_state(DeliveryOrderFSM.description_state)
    await state.update_data(date=m.text)

    message = await m.answer(
        "Укажите детали заказа или напишите \"Нет\""
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)


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

    if order.creator.telegram_username != m.from_user.username:
        order.creator.telegram_username = m.from_user.username
        await db_session.commit()
    if m.from_user.username is None:
        await m.answer(
            "❗️ Вы не указали имя пользвотеля в телеграмме, связь с другими пользователями бота будет невозможна"
        )

    await post_order(bot=m.bot, order=order, db_session=db_session)
    await m.answer(
        "Заказ успешно опубликован!"
    )
    await m.answer(
        text=order.get_description(),
        reply_markup=get_manage_order_markup(order.id)
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=s_data['prev_message'])
    except TelegramBadRequest:
        pass


@connection
async def start_sober_driver_order(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession):
    user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

    if user and (user.is_blocked or (not user.driver) or (not user.driver.is_moderated)):
        await c.answer("Вы не имеете права публикоавть заказы")
        return
    await state.set_state(SoberDriverFSM.from_state)

    message = await c.message.answer(
        "Укажите точку начала пути"
    )

    await state.update_data(prev_message=message.message_id)

    await c.answer()

    try:
        await c.message.delete()
    except TelegramBadRequest:
        pass


async def handle_from(m: types.Message, state: FSMContext):
    await state.set_state(SoberDriverFSM.dest_state)
    await state.update_data(start_point=m.text)

    message = await m.answer(
        "Теперь укажите конечную точку пути"
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)


async def handle_destination(m: types.Message, state: FSMContext):
    await state.set_state(SoberDriverFSM.price_state)
    await state.update_data(end_point=m.text)

    message = await m.answer(
        "Введите цену за заказ"
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)


async def handle_sdriver_price(m: types.Message, state: FSMContext):
    try:
        price = m.text
        await state.set_state(SoberDriverFSM.date_state)
        await state.update_data(price=price)

        message = await m.answer(
            "Введите дату и время заказа"
        )

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

        await state.update_data(prev_message=message.message_id)
    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )


async def handle_sdriver_date(m: types.Message, state: FSMContext):
    await state.set_state(SoberDriverFSM.description_state)
    await state.update_data(date=m.text)

    message = await m.answer(
        "Укажите детали заказа или напишите \"Нет\""
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)


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

    if order.creator.telegram_username != m.from_user.username:
        order.creator.telegram_username = m.from_user.username
        await db_session.commit()
    if m.from_user.username is None:
        await m.answer(
            "❗️ Вы не указали имя пользвотеля в телеграмме, связь с другими пользователями бота будет невозможна"
        )

    await post_order(bot=m.bot, order=order, db_session=db_session)

    await m.answer(
        "Заказ успешно опубликован!"
    )
    await m.answer(
        text=order.get_description(),
        reply_markup=get_manage_order_markup(order.id)
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=s_data['prev_message'])
    except TelegramBadRequest:
        pass


async def post_order(bot: Bot, order, db_session: AsyncSession):
    users = await UserDAO.get_drivers(session=db_session)

    for u in users:
        if u.id != order.creator.id:
            try:
                await bot.send_message(
                    chat_id=u.telegram_id,
                    text=order.get_description(),
                    reply_markup=get_accept_order_markup(order.id)
                )
            except TelegramForbiddenError:
                continue


@connection
async def start_free_order(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession):
    user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

    if user and (user.is_blocked or (not user.driver) or (not user.driver.is_moderated)):
        await c.answer("Вы не имеете права публикоавть заказы")
        return
    await state.set_state(FreeOrderFSM.description_state)

    message = await c.message.answer(
        "Введите детали заказа"
    )

    await state.update_data(prev_message=message.message_id)

    try:
        await c.message.delete()
    except TelegramBadRequest:
        pass


async def handle_free_description(m: types.Message, state: FSMContext):
    await state.set_state(FreeOrderFSM.price_state)
    await state.update_data(description=m.text[:199])

    message = await m.answer(
        "Введите цену за заказ"
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
    except TelegramBadRequest:
        pass

    await state.update_data(prev_message=message.message_id)


async def handle_free_price(m: types.Message, state: FSMContext):

    try:
        price = m.text
        await state.set_state(FreeOrderFSM.date_state)
        await state.update_data(price=price)

        message = await m.answer(
            "Введите дату и время заказа"
        )

        try:
            await m.delete()
            await m.bot.delete_message(chat_id=m.chat.id, message_id=(await state.get_data())['prev_message'])
        except TelegramBadRequest:
            pass

        await state.update_data(prev_message=message.message_id)
    except ValueError:
        await m.answer(
            "Необходимо ввести число! Попробуйте еще раз"
        )

@connection
async def handle_free_date(m: types.Message, state: FSMContext, db_session: AsyncSession):
    await state.update_data(date=m.text.strip()[:29])
    s_data = await state.get_data()
    await state.clear()


    user = await UserDAO.get_obj(session=db_session, telegram_id=m.from_user.id)

    order = await OrderDAO.add_order(
        date=s_data["date"],
        creator_id=user.id,
        session=db_session,
        order_type=OrderType.FREE_ORDER,
        description=s_data['description'],
        price=s_data['price']
    )

    if order.creator.telegram_username != m.from_user.username:
        order.creator.telegram_username = m.from_user.username
        await db_session.commit()
    if m.from_user.username is None:
        await m.answer(
            "❗️ Вы не указали имя пользвотеля в телеграмме, связь с другими пользователями бота будет невозможна"
        )
    if m.from_user.username is None:
        await m.answer(
            "❗️ Вы не указали имя пользвотеля в телеграмме, связь с другими пользователями бота будет невозможна"
        )

    await post_order(bot=m.bot, order=order, db_session=db_session)

    await m.answer(
        "Заказ успешно опубликован!"
    )
    await m.answer(
        text=order.get_description(),
        reply_markup=get_manage_order_markup(order.id)
    )

    try:
        await m.delete()
        await m.bot.delete_message(chat_id=m.chat.id, message_id=s_data['prev_message'])
    except TelegramBadRequest:
        pass



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

    dp.callback_query.register(start_free_order, F.data == "ordertype_5")
    dp.message.register(handle_free_description, StateFilter(FreeOrderFSM.description_state))
    dp.message.register(handle_free_price, StateFilter(FreeOrderFSM.price_state))
    dp.message.register(handle_free_date, StateFilter(FreeOrderFSM.date_state))

