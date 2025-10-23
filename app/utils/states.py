from aiogram.fsm.state import StatesGroup, State


class LoginStates(StatesGroup):
    waiting_username = State()
    waiting_password = State()
