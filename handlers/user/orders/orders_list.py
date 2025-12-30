from aiogram import types, F, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import OrderDAO, UserDAO
from database.utils import connection
from markups.user.order import get_accept_order_markup
from utils.paging.orders_paging import OrdersPaging


@connection
async def send_orders_list(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user = await UserDAO.get_user_with_cars(session=db_session, telegram_id=c.from_user.id)

    if user.driver:
        if user.driver.is_moderated:
            if user.cars:
                paging = OrdersPaging()

                await paging.get_queryset(db_session=db_session)
                await paging.get_current_page()

                await c.message.answer(
                    "Список заказов",
                    reply_markup=paging.get_reply_markup()
                )
            else:
                await c.answer(
                    "Сначала необходимо зарегистрировать автомобиль",
                    show_alert=True
                )
            await c.answer()
        else:
            await c.answer(
                "Дождитесь пока администрация одобрит вашу анкету",
                show_alert=True
            )
    else:
        await c.answer(
            "Сначала необходимо заполнить анкету водителя, чтобы принимать заказы",
            show_alert=True
        )


@connection
async def send_order_card(c: types.CallbackQuery, db_session: AsyncSession, *args):

    order_id = int(c.data.split('_')[1])

    order = await OrderDAO.get_obj(session=db_session, id=order_id)

    if order:
        await c.message.answer(
            text=order.get_description(),
            reply_markup=get_accept_order_markup(order_id)
        )
        await c.answer()
    else:
        await c.answer(
            "Ошибка, заказ не найден",
            show_alert=True
        )


@connection
async def accept_order(c: types.CallbackQuery, db_session: AsyncSession, *args):
    order_id = int(c.data.split('_')[1])

    order = await OrderDAO.get_obj(session=db_session, id=order_id)

    if order:
        if order.executor:
            await c.answer(
                "Этот заказ уже был принят",
                show_alert=True
            )
        else:
            user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

            order.executor = user
            await db_session.commit()

            await c.message.answer(
                "Заказ был успешно принят"
            )

            try:
                await c.bot.send_message(
                    chat_id=order.creator.telegram_id,
                    text="Ваш заказ был принят!"
                )
            except TelegramBadRequest:
                pass
    else:
        await c.answer(
            "Ошибка, заказ не найден",
            show_alert=True
        )


def register_orders_list_handlers(dp: Dispatcher):
    dp.callback_query.register(send_orders_list, F.data == "active_orders")
    OrdersPaging.register_paging_handlers(dp, "o")
    dp.callback_query.register(send_order_card, F.data.startswith("order_"))
    dp.callback_query.register(accept_order, F.data.startswith("acceptorder_"))
