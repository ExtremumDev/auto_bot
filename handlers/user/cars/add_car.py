from aiogram import types, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import CAR_PHOTO_PATH, CAR_VIDEO_PATH
from database.dao import UserDAO, CarDAO
from database.utils import connection
from fsm.user.car_manage import AddingCarFSM
from utils.enums import CarClass
from utils.utils import check_and_save_photo, check_and_save_video_message


@connection
async def start_car_registration(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    user = await UserDAO.get_user_with_cars(session=db_session, telegram_id=c.from_user.id)

    if user.driver:
        if user.cars and len(user.cars) >= 3:
            await c.answer(
                show_alert=True,
                text="Превышен лимит автомобилей!"
            )

        else:
            await state.set_state(AddingCarFSM.brand_state)
            await c.message.answer(
                "Введите марку автомобиля"
            )
            await c.answer()
    else:
        await c.message.answer(
            "Сначала необходимо заполнить анкету водтителя",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Перейти к заполнению", callback_data="fill_form")]
                ]
            )
        )


async def handle_brand(m: types.Message, state: FSMContext):
    await state.set_state(AddingCarFSM.model_state)
    await state.update_data(brand=m.text.strip()[:19])

    await m.answer(
        "Введите модель автомобиля"
    )


async def handle_model(m: types.Message, state: FSMContext):
    await state.set_state(AddingCarFSM.release_year_state)
    await state.update_data(model=m.text.strip()[:29])

    await m.answer(
        "Укажите год выпуска автомобиля"
    )



async def handle_release_year(m: types.Message, state: FSMContext):
    try:
        year = int(m.text)
        await state.set_state(AddingCarFSM.number_state)
        await state.update_data(year=year)

        await m.answer(
            "Введите государственный номер автомобиля"
        )
    except ValueError:
        await m.answer("Необходимо ввести число! Попробуйте еще раз")


async def handle_car_number(m: types.Message, state: FSMContext):
    # verification

    await state.set_state(AddingCarFSM.sts_state)
    await state.update_data(car_number=m.text[:29])

    await m.answer(
        "Введите серию и номер своего СТС РФ через пробел"
    )


async def handle_sts(m: types.Message, state: FSMContext):
    # verification

    await state.set_state(AddingCarFSM.car_class_state)
    await state.update_data(sts_number=m.text[:49])

    await m.answer(
        "Выберите класс вашего автомобиля:\n",
        reply_markup=CarClass.get_choice_by_passengers_number()
    )


async def handle_car_class(c: types.CallbackQuery, state: FSMContext):
    car_class_id = c.data.split('_')[1]

    await state.set_state(AddingCarFSM.photo_state)
    await state.update_data(car_class=car_class_id)

    await c.message.answer(
        "Пришлите фотографию автомобиля"
    )

    await c.answer()


async def handle_car_photo(m: types.Message, state: FSMContext):
    file_name = await check_and_save_photo(m, CAR_PHOTO_PATH, "Фотография_{user_id}_{datetime}")

    if file_name:
        await state.set_state(AddingCarFSM.video_message_state)
        await state.update_data(car_photo=file_name)

        await m.answer(
            "Приишлите видеособщение"
        )


@connection
async def handle_video_message(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    file_name = await check_and_save_video_message(m, CAR_VIDEO_PATH, "Видео_автомобиль_{user_id}_{datetime}")

    if file_name:
        await state.update_data(car_video=file_name)

        s_data = await state.get_data()
        await state.clear()

        user = await UserDAO.get_obj(session=db_session, telegram_id=m.from_user.id)

        car = await CarDAO.add(
            session=db_session,
            brand=s_data["brand"],
            model=s_data["model"],
            release_year=s_data["year"],
            car_number=s_data["car_number"],
            sts_number=s_data["sts_number"],
            car_class=s_data["car_class"],
            photo=s_data["car_photo"],
            video=s_data["car_video"],
            user_id=user.id
        )

        await m.answer("Автомобиль успешно добавлен!")


def register_add_car_handlers(dp: Dispatcher):
    dp.callback_query.register(
        start_car_registration,
        F.data == "add_car"
    )
    dp.message.register(
        handle_brand,
        StateFilter(AddingCarFSM.brand_state)
    )
    dp.message.register(handle_model, StateFilter(AddingCarFSM.model_state))
    dp.message.register(handle_release_year, StateFilter(AddingCarFSM.release_year_state))
    dp.message.register(handle_car_number, StateFilter(AddingCarFSM.number_state))
    dp.message.register(handle_sts, StateFilter(AddingCarFSM.sts_state))

    dp.callback_query.register(
        handle_car_class,
        F.data.startswith("carclass_"),
        StateFilter(AddingCarFSM.car_class_state)
    )

    dp.message.register(handle_car_photo, StateFilter(AddingCarFSM.photo_state))
    dp.message.register(handle_video_message, StateFilter(AddingCarFSM.video_message_state))
