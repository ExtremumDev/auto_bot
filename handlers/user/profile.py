from aiogram import types, Dispatcher, F
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import UserDAO
from database.utils import connection
from markups.user.profile import get_profile_markup
from utils.text import get_user_profile_descr


@connection
async def send_profile_info(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user = await UserDAO.get_user_with_cars(session=db_session, telegram_id=c.from_user.id)

    await c.message.answer(
        text=get_user_profile_descr(
            is_drive=user.driver,
            is_drive_confirmed=user.driver.is_moderated if user.driver else False,
            cars=user.cars
        ),
        reply_markup=get_profile_markup(is_has_driver=user.driver)
    )

    await c.answer()


def register_profile_handlers(dp: Dispatcher):
    dp.callback_query.register(send_profile_info, F.data == "my_profile")
