# bot/utils/states.py

from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    waiting_for_broadcast_text = State()