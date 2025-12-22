from .start import register_start_handlers
from .events import register_create_event_handlers
from .inititatives import register_manage_initiative_handlers
from .mailing import register_create_mailing_handlers
from .event_manage import register_event_manage_handlers


def register_admin_handlers(dp):
    register_start_handlers(dp)
    register_create_event_handlers(dp)
    register_manage_initiative_handlers(dp)
    register_create_mailing_handlers(dp)
    register_event_manage_handlers(dp)
