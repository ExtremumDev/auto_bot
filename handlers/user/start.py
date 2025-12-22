import datetime
from pathlib import Path

from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType, ContentType

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_fallback

from config import PASSPORTS_PHOTO_PATH, DRIVE_LICENSES_PATH
from database.utils import connection
from fsm.user.main import RegistrationFSM


async def check_and_save_photo(message: types.Message, save_path: Path, file_name_format: str) -> bool | str:
    """

    :param message:
    :param save_path:
    :param file_name_format:
    :return: if image correct and was saved - file name will be returned, else - false
    """
    if message.photo:
        file_name = file_name_format.format(user_id=message.from_user.id, datetime=datetime.datetime.now().strftime("%d-%m-%Y_%H-%M"))

        await message.bot.download(
            message.photo[-1].file_id,
            save_path / file_name
        )

        return file_name


    elif message.document:
        await message.answer(
            "Пожалуйста пришлите фотографию не как файл, а как картинку"
        )
    else:
        await message.answer(
            "Необходимо прислать фотографию! Попробуйте еще раз"
        )
    return False



@connection
async def start_cmd(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.clear()

    user = await UserDAO.get_obj(db_session, telegram_id=m.from_user.id)
    reg = False
    if not user:
        reg = True
        await UserDAO.register_user(
            db_session, m.from_user.id, m.from_user.username, False
        )
    else:
        if not user.has_private:
            reg = True

        if m.from_user.username != user.telegram_username:
            user.telegram_username = m.from_user.username
            await db_session.commit()

    if reg:
        await state.set_state(RegistrationFSM.name_state)
        await m.answer_photo(
            photo=types.FSInputFile("images/start_image.jpg"),
            caption="""
Приветстсвую! Я твой помощник в комьюнити RendezVous.\n\n Давай познакомимся. Как тебя зовут? Напиши имя и фамилию
"""
        )
    else:
        await m.answer(
            "Открыто главное меню",
            reply_markup=main_user_markup
        )

#-------------
# REGISTRATION
#-------------

async def handle_full_name(m: types.Message, state: FSMContext):
    await state.set_state(RegistrationFSM.phone_number_state)
    await state.update_data(full_name=m.text)

    await m.answer(
        "Введите свой номер телефона"
    )


async def handle_phone_number(m: types.Message, state: FSMContext):
    # verify phone number

    await state.set_state(RegistrationFSM.city_state)
    await state.update_data(phone=m.text)

    await m.answer(
        "Укажите город своего проживания"
    )


async def handle_city(m: types.Message, state: FSMContext):

    await state.set_state(RegistrationFSM.passport_state)
    await state.update_data(city=m.text)

    await m.answer(
        "Введите номер и серию своего паспорта через пробел",
    )


async def handle_passport(m: types.Message, state: FSMContext):
    # verify

    await state.set_state(RegistrationFSM.passport_photo_state)
    await state.update_data(passport_number=m.text)

    await m.answer(
        "Пришлите фотографию первой страницы своего паспорта",
    )


async def handle_passport_photo(m: types.Message, state: FSMContext):

    file_name = check_and_save_photo(m, PASSPORTS_PHOTO_PATH, "Паспорт_{user_id}_{datetime}")

    if file_name:

        await state.set_state(RegistrationFSM.drive_exp_state)
        await state.update_data(passport_photo=file_name)

        await m.answer(
            "Укажите свой стаж вождения(введите количество лет)",
        )


async def handle_drive_exp(m: types.Message, state: FSMContext):
    try:
        drive_exp = int(m.text)

        await state.set_state(RegistrationFSM.license_number_state)
        await state.update_data(drive_exp=drive_exp)

        await m.answer(
            "Теперь заполните данные о водительских праваз РФ. Введите серию и номер документа через пробел",
        )
    except ValueError:
        await m.answer("Необходимо ввести число! Попробуйте еще раз")


async def handle_license_number(m: types.Message, state: FSMContext):
    # verify

    await state.set_state(RegistrationFSM.license_photo_1_state)
    await state.update_data(license_number=m.text)

    await m.answer("Пришлите фотографию фронтальной стороны водительских прав")


async def handle_first_license_photo(m: types.Message, state: FSMContext):

    file_name = check_and_save_photo(m, DRIVE_LICENSES_PATH, "Права_Страница_1_{user_id}_{datetime}")
    if m.photo:
        await state.set_state(RegistrationFSM.license_photo_2_state)
        await state.update_data(passport_photo=file_name)

        await m.answer(
            "Отлично! Теперь пришлите фотографию задней стороны водительских прав",
        )


async def handle_second_license_photo(m: types.Message, state: FSMContext):

    file_name = check_and_save_photo(m, DRIVE_LICENSES_PATH, "Права_Страница_2_{user_id}_{datetime}")
    if m.photo:
        await state.set_state(RegistrationFSM.license_photo_2_state)
        await state.update_data(passport_photo=file_name)

        await m.answer(
            "Отлично! Теперь пришлите фотографию задней стороны водительских прав",
        )


    elif m.document:
        await m.answer(
            "Пожалйста пришлите фотографию не как файл, а как картинку"
        )
    else:
        await m.answer(
            "Необходимо прислать фотографию! Попробуйте еще раз"
        )


def register_user_start_handlers(dp: Dispatcher):
    dp.message.register(
        start_cmd,
        CommandStart(),
        StateFilter('*')
    )

    dp.message.register(handle_full_name, StateFilter(RegistrationFSM.full_name_state))
    dp.message.register(handle_phone_number, StateFilter(RegistrationFSM.phone_number_state))
    dp.message.register(handle_city, StateFilter(RegistrationFSM.city_state))
    dp.message.register(handle_passport, StateFilter(RegistrationFSM.passport_state))
    dp.message.register(handle_passport_photo, StateFilter(RegistrationFSM.passport_photo_state))
    dp.message.register(handle_drive_exp, StateFilter(RegistrationFSM.drive_exp_state))
    dp.message.register(handle_license_number, StateFilter(RegistrationFSM.license_number_state))
    dp.message.register(handle_first_license_photo, StateFilter(RegistrationFSM.license_photo_1_state))
    dp.message.register(handle_second_license_photo, StateFilter(RegistrationFSM.license_photo_2_state))