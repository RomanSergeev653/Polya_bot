from aiogram.fsm.state import State, StatesGroup


class AddCategoryStates(StatesGroup):
    title = State()


class AddProductStates(StatesGroup):
    category_id = State()
    photo_id = State()
    title = State()
    description = State()
    price = State()
    sort_order = State()
    confirm = State()


class EditProductStates(StatesGroup):
    waiting_value = State()


class EditCategorySortStates(StatesGroup):
    sort_order = State()


class EditContactsStates(StatesGroup):
    text = State()
