from aiogram.fsm.state import StatesGroup, State


class RegistrationFSM(StatesGroup):
    full_name_state = State()
    phone_number_state = State()
    city_state = State()

    passport_state = State()
    passport_photo_state = State()

    drive_exp_state = State()

    license_number_state = State()
    license_series_state = State()
    license_photo_1_state = State()
    license_photo_2_state = State()
