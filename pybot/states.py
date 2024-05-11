from aiogram.fsm.state import StatesGroup, State


class AdminStateGroup(StatesGroup):
    sending_telethon_session = State()
    sending_json_session = State()


class MainStatesGroup(StatesGroup):
    sending_bitpapa_code = State()
