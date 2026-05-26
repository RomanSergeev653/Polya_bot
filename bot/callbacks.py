from aiogram.filters.callback_data import CallbackData


class NoopCallback(CallbackData, prefix="noop"):
    pass


class MenuCallback(CallbackData, prefix="menu"):
    action: str  # contacts


class CategoryCallback(CallbackData, prefix="cat"):
    category_id: int


class CarouselCallback(CallbackData, prefix="carousel"):
    category_id: int
    index: int


class BackToMenuCallback(CallbackData, prefix="back_menu"):
    pass


class OrderCallback(CallbackData, prefix="order"):
    product_id: int


# --- Admin ---


class AdminMenuCallback(CallbackData, prefix="adm"):
    action: str  # categories, products, contacts, back


class AdminCategoryCallback(CallbackData, prefix="adm_cat"):
    action: str  # list, add, view, delete, delete_confirm, sort
    category_id: int = 0


class AdminProductListCallback(CallbackData, prefix="adm_pl"):
    category_id: int
    page: int = 0


class AdminProductCallback(CallbackData, prefix="adm_p"):
    action: str  # view, delete, delete_confirm, edit_menu
    product_id: int = 0


class AdminProductEditCallback(CallbackData, prefix="adm_pe"):
    field: str  # photo, category, title, description, price, sort
    product_id: int


class AdminProductAddCallback(CallbackData, prefix="adm_pa"):
    action: str  # category, confirm, cancel
    category_id: int = 0


class AdminConfirmCallback(CallbackData, prefix="adm_ok"):
    action: str
    entity_id: int
