
from config import AdminsSettings
from database.utils import connection


class AdminFilter:

    def __call__(self, telegram_obj, *args, **kwargs):
        return telegram_obj.from_user.id in AdminsSettings.ADMIN_ID or telegram_obj.from_user.id in AdminsSettings.MAIN_ADMIN_ID

class MainAdminFilter:

    def __call__(self, telegram_obj, *args, **kwargs):
        return telegram_obj.from_user.id in AdminsSettings.MAIN_ADMIN_ID

