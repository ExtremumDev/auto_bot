from .admin import register_admin_handlers
from .extra import register_extra_handlers
from .user import register_user_handlers


def register_all_handlers(dp):
    register_admin_handlers(dp)
    register_user_handlers(dp)

    register_extra_handlers(dp)
