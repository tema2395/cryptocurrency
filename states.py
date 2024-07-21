from aiogram.fsm.state import StatesGroup, State


class CryptoStates(StatesGroup):
    waiting_for_crypto = State()
    waitign_for_time = State()
    
    