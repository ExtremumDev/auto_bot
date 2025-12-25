from aiogram import types, Dispatcher
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from config import PASSPORTS_PHOTO_PATH, DRIVE_LICENSES_PATH
from database.dao import UserDAO, DriverDAO
from database.utils import connection
from fsm.user.main import RegistrationFSM
from markups.user.main import get_main_markup
from utils.utils import check_and_save_photo


@connection
async def start_cmd(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.clear()

    user = await UserDAO.get_obj(db_session, telegram_id=m.from_user.id)
    if user:
        if user.driver:
            await m.answer(
                "Здравствуйте",
                reply_markup=get_main_markup()
            )
        else:
            await state.set_state(RegistrationFSM.full_name_state)
            await m.answer(
                "Приветствую! Необходимо зарегистрироваться. Введите свое ФИО"
            )

    else:
        await UserDAO.add(
            db_session,
            telegram_id=m.from_user.id,
            telegram_username=m.from_user.username
        )

        await state.set_state(RegistrationFSM.full_name_state)
        await m.answer(
            "Приветствую! Необходимо зарегистрироваться. Введите свое ФИО"
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
    await state.update_data(passport_number=m.text.strip())

    await m.answer(
        "Пришлите фотографию первой страницы своего паспорта",
    )


async def handle_passport_photo(m: types.Message, state: FSMContext):

    file_name = await check_and_save_photo(m, PASSPORTS_PHOTO_PATH, "Паспорт_{user_id}_{datetime}")

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
    await state.update_data(license_number=m.text.strip())

    await m.answer("Пришлите фотографию фронтальной стороны водительских прав")


async def handle_first_license_photo(m: types.Message, state: FSMContext):

    file_name = await check_and_save_photo(m, DRIVE_LICENSES_PATH, "Права_Страница_1_{user_id}_{datetime}")
    if m.photo:
        await state.set_state(RegistrationFSM.license_photo_2_state)
        await state.update_data(license_photo_1=file_name)

        await m.answer(
            "Отлично! Теперь пришлите фотографию задней стороны водительских прав",
        )


@connection
async def handle_second_license_photo(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):

    file_name = await check_and_save_photo(m, DRIVE_LICENSES_PATH, "Права_Страница_2_{user_id}_{datetime}")
    if file_name:
        await state.update_data(license_photo_2=file_name)

        s_data = await state.get_data()
        await state.clear()

        driver = await DriverDAO.add(
            session=db_session,
            full_name=s_data['full_name'][:79],
            phone_number=s_data['phone'][:11],
            city=s_data['city'][:19],
            passport_number=s_data['passport_number'][:14],
            passport_photo=s_data['passport_photo'],
            drive_exp=s_data['drive_exp'],
            license_number=s_data['license_number'][:9],
            license_photo_1=s_data['license_photo_1'],
            license_photo_2=s_data['license_photo_2']
        )

        user = await UserDAO.get_obj(session=db_session, telegram_id=m.from_user.id)
        user.driver = driver
        await db_session.commit()

        await m.answer(
            "Отлично! Регистрация прошла успешно. Теперь время добавить даные автомобиля",
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