from handlers.user.cars.add_car import register_add_car_handlers
from .cars.car_manage import register_car_manage_handlers
from .start import register_user_start_handlers


def register_user_handlers(dp):
    register_user_start_handlers(dp)

    register_add_car_handlers(dp)
    register_car_manage_handlers()

