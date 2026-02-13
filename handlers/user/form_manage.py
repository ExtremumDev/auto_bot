from aiogram import types, F, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from config import PASSPORTS_PHOTO_PATH, DRIVE_LICENSES_PATH
from database.dao import DriverDAO, UserDAO
from database.utils import connection
from fsm.user.main import EditFormFSM
from markups.admin.user_manage import get_moderate_driver_markup
from markups.user.profile import get_forms_list_markup, form_edition_markup
from utils.messaging import send_message_to_admins
from utils.text import get_driver_form_text
from utils.utils import check_and_save_photo, get_user_form_field_name


@connection
async def send_forms_history(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)
    user_driver_forms = await DriverDAO.get_all_user_forms(session=db_session, user_id=user.id)

    await c.message.answer(
        "История редактирования анкеты. Нажмите на нужную версию, чтобы посмотреть подробнее",
        reply_markup=get_forms_list_markup(user_driver_forms, False)
    )


@connection
async def send_driver_form(c: types.CallbackQuery, db_session: AsyncSession, *args):
    driver_id = int(c.data.split('_')[1])

    driver = await DriverDAO.get_obj(session=db_session, id=driver_id)

    await c.message.answer(
        get_driver_form_text(driver),
    )


@connection
async def ask_what_edit(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    user = await UserDAO.get_obj(session=db_session, telegram_id=c.from_user.id)

    if user.driver:
        if user.driver.is_moderated:
            await c.message.answer(
                "Выберите, что хотите отредактировать",
                reply_markup=form_edition_markup
            )
            await c.answer()

        else:
            await c.answer(
                "Ваша последняя версия анкеты еще не была рассмотрена администраторами. Вы пока не можете создать новую",
                show_alert=True
            )
    else:
        await c.answer(
            "Вы еще не заполняли анкету",
            show_alert=True
        )


async def ask_new_value(c: types.CallbackQuery, state: FSMContext):
    editing = c.data.split('_')[1]

    await state.set_state(EditFormFSM.edit_state)

    current_key = ""

    match editing:
        case "name":
            current_key = "full_name"
            await c.message.answer("Введите ФИО")
        case "passport":
            current_key = "passport_number"
            await c.message.answer(
                "Введите серию и номер своего паспорта через пробел"
            )
        case "license":
            current_key="license_number"
            await c.message.answer("Введите серию и номер водительских прав через пробел")
        case "phone":
            current_key = "phone_number"
            await c.message.answer("Введите номер телефона")

    await state.update_data(current_key=current_key, editing=editing, form_data={})

    await c.answer()


async def handle_value(m: types.Message, state: FSMContext):
    s_data = await state.get_data()
    current_key = s_data['current_key']

    if current_key == "passport_photo":
        value = await check_and_save_photo(m, PASSPORTS_PHOTO_PATH, "Паспорт_{user_id}_{datetime}")

    elif current_key == "license_photo_1":
        value = await check_and_save_photo(m, DRIVE_LICENSES_PATH, "Права_Страница_1_{user_id}_{datetime}")
    elif current_key == "license_photo_2":
        value = await check_and_save_photo(m, DRIVE_LICENSES_PATH, "Права_Страница_2_{user_id}_{datetime}")
    else:
        value = m.text

    s_data['form_data'][current_key] = value

    await state.set_data(s_data)


    match s_data['editing']:
        case "name" | "phone":
            await save_new_driver_form(m.from_user.id, s_data['form_data'])
            await state.clear()
        case "passport":
            if current_key == "passport_number":
                await state.update_data(current_key="passport_photo")
                await m.answer("Пришлите фотографию первой страницы своего паспорта")
            elif current_key == "passport_photo":
                await save_new_driver_form(m.from_user.id, s_data['form_data'])
                await state.clear()
        case "license":
            if current_key == "license_number":
                await state.update_data(current_key="license_photo_1")
                await m.answer("Пришлите фотографию лицевой стороны водительских прав")
            elif current_key == "license_photo_1":
                await state.update_data(current_key="license_photo_2")
                await m.answer("Теперь пришлите фотографию задней стороны водительских прав")
            elif current_key == "license_photo_2":
                await save_new_driver_form(m.from_user.id, s_data['form_data'])
                await state.clear()

@connection
async def save_new_driver_form(user_id: int, data, db_session: AsyncSession):
    user = await UserDAO.get_obj(session=db_session, telegram_id=user_id)
    driver = user.driver

    changes_info_text = "\nИзменено:"

    for k, v in data.items():
        driver.__setattr__(k, v)
        changes_info_text += f"\n- {get_user_form_field_name(k)}"

    new_driver = await DriverDAO.add(
        session=db_session,
        full_name=driver.full_name,
        phone_number=driver.phone_number,
        city=driver.city,
        passport_number=driver.passport_number,
        passport_photo=driver.passport_photo,
        drive_exp=driver.drive_exp,
        license_number=driver.license_number,
        license_photo_1=driver.license_photo_1,
        license_photo_2=driver.license_photo_2,
        user_id=user.id,
        is_moderated=False
    )

    user.driver = new_driver
    await db_session.flush((user,))

    await send_message_to_admins(
        message="Пользователь отредактировал анкету, ожидается модерация" + changes_info_text,
        reply_markup=get_moderate_driver_markup(user.id)

    )
    await bot.send_message(
        user_id,
        "Новая версия анкеты принята! Новая версия отправлена на модерацию администраторам"
    )


def register_forms_manage_handlers(dp: Dispatcher):
    dp.callback_query.register(send_forms_history, F.data=="forms_history")
    dp.callback_query.register(send_driver_form, F.data.startswith("showmyform_"))

    dp.callback_query.register(ask_what_edit, F.data == "edit_form")
    dp.callback_query.register(ask_new_value, F.data.startswith("formedit_"))
    dp.message.register(handle_value, StateFilter(EditFormFSM.edit_state))
