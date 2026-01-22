from handlers.admin.mailing import register_mailing_handlers
from handlers.admin.main import register_main_admin_handlers
from handlers.admin.orders_manage import register_admin_orders_manage_handlers
from handlers.admin.rules import register_edit_rules_handlers
from handlers.admin.users_manage import register_users_manage_handers


def register_admin_handlers(dp):
    register_main_admin_handlers(dp)
    register_edit_rules_handlers(dp)
    register_users_manage_handers(dp)
    register_mailing_handlers(dp)
    register_admin_orders_manage_handlers(dp)
