from aiogram.fsm.state import StatesGroup, State


class AdminStateGroup(StatesGroup):
    sending_telethon_session = State()
