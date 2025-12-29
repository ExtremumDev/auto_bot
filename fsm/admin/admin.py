from aiogram.fsm.state import State, StatesGroup


class EditRulesFSM(StatesGroup):
    rules_text_state = State()


class MailingFSM(StatesGroup):
    text_state = State()
    photo_state = State()
