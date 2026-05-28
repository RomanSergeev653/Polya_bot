from aiogram.fsm.state import State, StatesGroup


class AddCategoryStates(StatesGroup):
    title = State()


class AddProductStates(StatesGroup):
    category_id = State()
    photos = State()
    title = State()
    description = State()
    price = State()
    sort_order = State()
    confirm = State()


class EditProductStates(StatesGroup):
    waiting_value = State()


class AddProductPhotoStates(StatesGroup):
    waiting_photo = State()


class EditCategorySortStates(StatesGroup):
    sort_order = State()


class EditContactsStates(StatesGroup):
    text = State()


class EditMenuTextStates(StatesGroup):
    text = State()


class EditOrderContactStates(StatesGroup):
    value = State()
