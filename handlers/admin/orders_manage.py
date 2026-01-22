from aiogram import types, F, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import OrderDAO
from database.utils import connection
from filters.users import MainAdminFilter
from markups.user.order import get_manage_order_markup
from utils.paging.orders_paging import OrdersPaging


@connection
async def send_orders_list(c: types.CallbackQuery, db_session: AsyncSession, *args):
    paging = OrdersPaging()
    await paging.get_queryset(db_session=db_session)
    await paging.get_current_page()

    await c.message.answer(
        text="Выберете заказ",
        reply_markup=paging.get_reply_markup()
    )


@connection
async def send_order_card(c: types.CallbackQuery, db_session: AsyncSession, *args):

    order_id = int(c.data.split('_')[1])

    order = await OrderDAO.get_obj(session=db_session, id=order_id)

    if order:

        await c.message.answer(
            text=order.get_description(),
            reply_markup=get_manage_order_markup(order_id)
        )
    else:
        await c.answer(
            "Ошибка, заказ не найден",
            show_alert=True
        )


def register_admin_orders_manage_handlers(dp: Dispatcher):
    dp.callback_query.register(send_orders_list, MainAdminFilter(), F.data == "admin_orders_manage")
    OrdersPaging.register_paging_handlers(dp, "o")

    dp.callback_query.register(send_order_card, MainAdminFilter(), F.data.startswith("order_"))
