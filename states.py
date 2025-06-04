from aiogram.fsm.state import StatesGroup, State

class CreateCard(StatesGroup):
    front = State()
    back = State()

class EditCard(StatesGroup):
    new_front = State()
    new_back = State()

class Study(StatesGroup):
    waiting_for_answer = State()
    waiting_for_ease = State()
