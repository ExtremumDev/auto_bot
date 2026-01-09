from aiogram.fsm.state import State, StatesGroup


class CrossCityOrderFSM(StatesGroup):

    from_state = State()

    destination_state = State()

    speed_state = State()
    date_state = State()

    time_state = State()

    passengers_state = State()
    car_class_state = State()

    intermediate_points_state = State()


class PlaceOrderFSM(StatesGroup):
    settlement_state = State()
    description_state = State()


class DeliveryOrderFSM(PlaceOrderFSM):
    pass


class SoberDriverFSM(StatesGroup):
    from_state = State()
    dest_state = State()
    description_state = State()
