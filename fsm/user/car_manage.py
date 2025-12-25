from aiogram.fsm.state import StatesGroup, State


class AddingCarFSM(StatesGroup):
    brand_state = State()
    model_state = State()
    release_year_state = State()
    number_state = State()
    sts_state = State()
    car_class_state = State()
    photo_state = State()
    video_message_state = State()

