from aiogram import types, Dispatcher, F
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import UserDAO
from database.utils import connection
from markups.user.profile import get_profile_markup
from utils.text import get_user_profile_descr


async def profile_callback(c: types.CallbackQuery):
    await send_profile_info(c.message)


@connection
async def send_profile_info(m: types.Message, db_session: AsyncSession, *args):
    user = await UserDAO.get_user_with_cars(session=db_session, telegram_id=m.from_user.id)

    await m.answer(
        text=get_user_profile_descr(
            is_drive=user.driver,
            is_drive_confirmed=user.driver.is_moderated if user.driver else False,
            cars=user.cars,
            orders_published=user.orders_published,
            orders_accepted=user.accepted_orders_count,
            orders_given=user.orders_given,
        ),
        reply_markup=get_profile_markup(is_has_driver=user.driver)
    )





def register_profile_handlers(dp: Dispatcher):
    dp.callback_query.register(profile_callback, F.data == "my_profile")
    dp.message.register(send_profile_info, F.text == "👤 Личный кабиент")
