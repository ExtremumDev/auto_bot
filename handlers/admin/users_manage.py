from aiogram import types, F, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.strategy import FSMStrategy
from sqlalchemy.ext.asyncio import AsyncSession

from config import AdminsSettings, PASSPORTS_PHOTO_PATH, DRIVE_LICENSES_PATH
from database.dao import UserDAO, DriverDAO
from database.utils import connection
from filters.users import AdminFilter, MainAdminFilter
from fsm.admin.users_manage import ConfirmAdministratorFSM
from markups.admin.user_manage import get_main_user_manage_markup, get_approve_form_markup
from markups.user.profile import get_forms_list_markup
from utils.paging.users_paging import UsersPaging
from utils.text import get_user_profile_descr, get_driver_form_text


@connection
async def send_users_list(c: types.CallbackQuery, db_session: AsyncSession, *args):
    paging = UsersPaging()
    await paging.get_queryset(db_session=db_session)
    await paging.get_current_page()

    await c.message.answer(
        "Выберите пользователя👇",
        reply_markup=paging.get_reply_markup()
    )


@connection
async def send_user_card(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])

    user = await UserDAO.get_user_with_cars(db_session, id=user_id)

    await c.message.answer(
        get_user_profile_descr(
            user.driver,
            user.driver.is_moderated if user.driver else False,
            user.cars
        ),
        reply_markup=get_main_user_manage_markup(user_id, user.is_blocked, user.is_admin, c.from_user.id in AdminsSettings.MAIN_ADMIN_ID)
    )

    await c.answer()


@connection
async def block_user(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])

    user = await UserDAO.get_user_with_cars(db_session, id=user_id)
    user.is_blocked = True

    await db_session.commit()

    await c.message.edit_reply_markup(
        reply_markup=get_main_user_manage_markup(user_id, user.is_blocked, c.from_user.id in AdminsSettings.MAIN_ADMIN_ID)
    )
    await c.answer("Пользователь временно заблокирован", show_alert=True)


@connection
async def unblock_user(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])

    user = await UserDAO.get_user_with_cars(db_session, id=user_id)
    user.is_blocked = False

    await db_session.commit()

    await c.message.edit_reply_markup(
        reply_markup=get_main_user_manage_markup(user_id, user.is_blocked, c.from_user.id in AdminsSettings.MAIN_ADMIN_ID)
    )
    await c.answer("Пользователь успешно разблокирован", show_alert=True)


@connection
async def send_user_driver_form(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])

    user = await UserDAO.get_user_with_cars(db_session, id=user_id)

    if user.driver:

        await c.message.answer_photo(
            photo=types.FSInputFile(
                PASSPORTS_PHOTO_PATH / user.driver.passport_photo
            ),
            caption="Фото паспорта"
        )

        await c.message.answer_photo(
            photo=types.FSInputFile(
                DRIVE_LICENSES_PATH / user.driver.license_photo_1
            )
        )
        await c.message.answer_photo(
            photo=types.FSInputFile(
                DRIVE_LICENSES_PATH / user.driver.license_photo_2
            ),
            caption="Водительские права"
        )
        await c.message.answer(
            get_driver_form_text(user.driver),
            reply_markup=get_approve_form_markup(user_id, user.driver.is_moderated)
        )
    else:
        await c.answer("Данный пользователь еще не заполнял анкету")


@connection
async def approve_user_driver_form(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])

    user = await UserDAO.get_user_with_cars(db_session, id=user_id)

    if user.driver:
        if user.driver.is_moderated:
            await c.answer(
                "Анкета уже была одобрена",
                show_alert=True
            )
        else:
            user.driver.is_moderated = True
            await db_session.commit()

            await c.message.edit_reply_markup(
                reply_markup=get_approve_form_markup(user_id, user.driver.is_moderated)
            )

            try:
                await c.bot.send_message(
                    chat_id=user.telegram_id,
                    text="Ваша анкета водителя была одобрена администраторами. Теперь время добавить автомобиль",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="Добавить автомобиль", callback_data="add_car")],
                            [types.InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
                        ]
                    )
                )
            except TelegramBadRequest:
                pass

            await c.answer(
                "Анкета успешно одобрена!",
                show_alert=True
            )
    else:
        await c.answer(
            "Не найдено заполненной анкеты пользователя",
            show_alert=True
        )


@connection
async def ask_confirm_administrator(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])

    user = await UserDAO.get_obj(session=db_session, id=user_id)

    if user.is_admin:
        await c.answer(
            "Пользоваетль уже является администратором",
            show_alert=True
        )
    else:
        await state.set_state(ConfirmAdministratorFSM.confirm_state)
        await state.update_data(user_id=user_id)

        await c.message.answer(
            "Подвердите действие",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Лишить администраторских прав"
                            if user.is_admin else "Сделать пользователя администратором",
                            callback_data="confirm"
                        )
                    ]
                ]
            )
        )
        await c.answer()


@connection
async def set_administrator(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    s_data = await state.get_data()
    await state.clear()

    user_id = s_data['user_id']

    user = await UserDAO.get_obj(session=db_session, id=user_id)

    if user.is_admin:
        user.is_admin = False
        AdminsSettings.remove_admin(user.telegram_id)

        await c.message.answer(
            "Пользователь больше не является администратором"
        )
    else:
        user.is_admin = True
        AdminsSettings.add_admin(user.telegram_id)
        await c.message.answer(
            "Пользователь теперь является администратором"
        )

    await db_session.commit()

    await c.answer()


@connection
async def send_user_forms_history(c: types.CallbackQuery, db_session: AsyncSession):
    user_id = int(c.data.split('_')[1])

    user = await UserDAO.get_obj(session=db_session, id=user_id)
    user_driver_forms = await DriverDAO.get_all_user_forms(session=db_session, user_id=user.id)

    await c.message.answer(
        "История редактирования анкеты. Нажмите на нужную версию, чтобы посмотреть подробнее",
        reply_markup=get_forms_list_markup(user_driver_forms)
    )


@connection
async def send_form_version(c: types.CallbackQuery, db_session: AsyncSession, *args):
    driver_id = int(c.data.split('_')[1])
    driver = await DriverDAO.get_obj(session=db_session, id=driver_id)

    await c.message.answer(
        get_driver_form_text(driver),
        reply_markup=get_approve_form_markup(driver.id, driver.is_moderated)
    )


def register_users_manage_handers(dp: Dispatcher):
    dp.callback_query.register(send_users_list, F.data == "users_manage", AdminFilter())
    UsersPaging.register_paging_handlers(dp, 'um')

    dp.callback_query.register(send_user_card, F.data.startswith("usermanage_"), AdminFilter())

    dp.callback_query.register(block_user, F.data.startswith("blockuser_"), AdminFilter())
    dp.callback_query.register(unblock_user, F.data.startswith("unblockuser_"), AdminFilter())

    dp.callback_query.register(send_user_driver_form, F.data.startswith("showform_"), AdminFilter())

    dp.callback_query.register(approve_user_driver_form, F.data.startswith("approve_"), AdminFilter())

    dp.callback_query.register(ask_confirm_administrator, F.data.startswith("changerights_"), MainAdminFilter())
    dp.callback_query.register(set_administrator, F.data.startswith("confirm"), StateFilter(ConfirmAdministratorFSM.confirm_state))

    dp.callback_query.register(send_user_forms_history, F.data.startswith("showformh_"), AdminFilter())
    dp.callback_query.register(send_form_version, F.data.startswith("showformvers_"), AdminFilter())
