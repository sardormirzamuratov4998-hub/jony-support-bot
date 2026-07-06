from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    name = State()
    phone = State()
    branch = State()


class AdminSearch(StatesGroup):
    query = State()


class AdminEditProfile(StatesGroup):
    waiting_value = State()


class AdminGroupForm(StatesGroup):
    # Admin tomonidan guruh ma'lumotlarini almashtirish (edit)
    name = State()
    branch = State()
    day_type = State()
    time = State()


class SupportAddGroup(StatesGroup):
    name = State()
    branch = State()
    day_type = State()
    time = State()


class ExaminerSearch(StatesGroup):
    query = State()
