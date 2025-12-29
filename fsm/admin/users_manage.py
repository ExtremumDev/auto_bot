from aiogram.fsm.state import StatesGroup, State


class ConfirmAdministratorFSM(StatesGroup):
    confirm_state = State()
