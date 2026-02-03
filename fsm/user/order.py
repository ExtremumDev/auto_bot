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

    nt_distance_state = State()
    rf_distance_state = State()

    price_state = State()
    description_state = State()


class PlaceOrderFSM(StatesGroup):
    settlement_state = State()
    price_state = State()
    description_state = State()
    date_state = State()


class DeliveryOrderFSM(PlaceOrderFSM):
    pass


class SoberDriverFSM(StatesGroup):
    from_state = State()
    dest_state = State()
    price_state = State()
    description_state = State()
    date_state = State()


class FreeOrderFSM(StatesGroup):
    description_state = State()
    date_state = State()
