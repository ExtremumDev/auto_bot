from aiogram import types, F, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import OrderDAO, UserDAO
from database.utils import connection
from markups.user.order import get_accept_order_markup, get_give_order_markup
from utils.enums import OrderStatus
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

                if paging.queryset:
                    for i in range(len(paging.queryset)):
                        o = paging.queryset[i]

                        reply_markup = get_accept_order_markup(o.id)
                        if i + 1 == len(paging.queryset):
                            reply_markup.inline_keyboard.extend(
                                types.InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [types.InlineKeyboardButton(text="Показать больше заказов",
                                                                    callback_data="onext_0")]
                                    ]
                                ).inline_keyboard
                            )

                        await c.message.answer(
                            text=o.get_description(),
                            reply_markup=reply_markup
                        )
                else:
                    await c.answer(
                        "Не найдено больше заказов"
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
async def next_page(c: types.CallbackQuery, db_session: AsyncSession):
    page = int(c.data.split('_')[1])

    paging = OrdersPaging(page=page)

    await paging.get_queryset(db_session=db_session)
    await paging.create_next_page()

    if paging.queryset:
        for i in range(len(paging.queryset)):
            o = paging.queryset[i]

            reply_markup = get_accept_order_markup(o.id)
            if i + 1  == len(paging.queryset):
                reply_markup.inline_keyboard.extend(
                    types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="Показать больше заказов", callback_data=f"onext_{page+1}")]
                        ]
                    ).inline_keyboard
                )

            await c.message.answer(
                text=o.get_description(),
                reply_markup=reply_markup
            )
    else:
        await c.answer(
            "Не найдено больше заказов"
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

    order = await OrderDAO.get_order_with_accepted(session=db_session, id=order_id)

    if order:
        if order.order_status != OrderStatus.SEARCHING:
            await c.answer(
                "Этот заказ уже отдан",
                show_alert=True
            )
        else:
            user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

            if not user in order.responded:


                order.responded.append(user)
                await db_session.commit()

                await c.message.answer(
                    f"Заказ был принят. Чат с создателем заказа @{order.creator.telegram_username}"
                )

                try:
                    await c.bot.send_message(
                        chat_id=order.creator.telegram_id,
                        text=order.get_description()
                    )
                    await c.bot.send_message(
                        chat_id=order.creator.telegram_id,
                        text=f"👆 Ваш заказ был принят пользователем @{user.telegram_username}",
                        reply_markup=get_give_order_markup(order_id, user.id)
                    )
                except TelegramBadRequest:
                    pass
            else:
                await c.answer("Вы уже принимали этот заказ")
    else:
        await c.answer(
            "Ошибка, заказ не найден",
            show_alert=True
        )


@connection
async def give_order_to_executor(c: types.CallbackQuery, db_session: AsyncSession, *args):
    c_data = c.data.split('_')
    order_id, user_id = int(c_data[1]), int(c_data[2])

    order = await OrderDAO.get_order_with_accepted(session=db_session, id=order_id)

    if order:
        if order.order_status != OrderStatus.SEARCHING:
            await c.answer(
                "Этот заказ уже отдан",
                show_alert=True
            )
        else:
            executor = await UserDAO.get_obj(session=db_session, id=user_id)

            order.order_status = OrderStatus.ACCEPTED.value
            order.executor = executor
            order.responded.clear()
            await db_session.commit()

            await c.message.answer(
                f"Заказ был успешно отдан пользователю @{executor.telegram_username}"
            )

            try:
                await c.bot.send_message(
                    chat_id=executor.telegram_id,
                    text=f"Создатель заказа @{c.from_user.username} отдал вам его на исполнение \n\nИнформация по заказу👇",
                )
                await c.bot.send_message(
                    chat_id=executor.telegram_id,
                    text=order.get_description()
                )
            except TelegramBadRequest:
                pass
    else:
        await c.answer(
            "Ошибка, заказ не найден",
            show_alert=True
        )


@connection
async def delete_order(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    order_id = int(c.data.split('_')[1])

    order = await OrderDAO.get_order_with_accepted(session=db_session, id=order_id)

    if order:

        await db_session.delete(order)
        await db_session.commit()

        await c.message.answer(
            f"Заказ был успешно удалён"
        )
        await c.answer()

    else:
        await c.answer(
            "Ошибка, заказ не найден",
            show_alert=True
        )


def register_orders_list_handlers(dp: Dispatcher):
    dp.callback_query.register(send_orders_list, F.data == "active_orders")
    dp.callback_query.register(next_page, F.data.startswith("onext_"))
    OrdersPaging.register_paging_handlers(dp, "o")
    dp.callback_query.register(send_order_card, F.data.startswith("order_"))
    dp.callback_query.register(accept_order, F.data.startswith("acceptorder_"))
    dp.callback_query.register(give_order_to_executor, F.data.startswith("giveorder_"))
    dp.callback_query.register(delete_order, F.data.startswith("delorder_"))
