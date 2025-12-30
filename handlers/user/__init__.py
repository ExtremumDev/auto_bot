from .cars.add_car import register_add_car_handlers
from .form_manage import register_forms_manage_handlers
from .orders.orders_list import register_orders_list_handlers
from .profile import register_profile_handlers
from .cars.car_manage import register_car_manage_handlers
from .orders.new_cross_city_order import register_new_cross_city_order_handlers
from .main import register_main_handlers
from .orders.new_order import register_orders_handlers
from .start import register_user_start_handlers


def register_user_handlers(dp):
    register_user_start_handlers(dp)

    register_main_handlers(dp)

    register_add_car_handlers(dp)
    register_car_manage_handlers(dp)
    register_profile_handlers(dp)
    register_new_cross_city_order_handlers(dp)
    register_orders_handlers(dp)
    register_forms_manage_handlers(dp)
    register_orders_list_handlers(dp)

