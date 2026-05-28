from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import (
    AdminCategoryCallback,
    AdminConfirmCallback,
    AdminMenuCallback,
    AdminProductAddCallback,
    AdminProductCallback,
    AdminProductEditCallback,
    AdminProductListCallback,
    AdminProductPhotoCallback,
)
from bot.db.queries import Category, Product, ProductPhoto

PRODUCTS_PER_PAGE = 5


def admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📂 Категории", callback_data=AdminMenuCallback(action="categories").pack())
    builder.button(text="📦 Товары", callback_data=AdminMenuCallback(action="products").pack())
    builder.button(text="📝 Текст меню", callback_data=AdminMenuCallback(action="menu_text").pack())
    builder.button(text="💬 Контакт для заказа", callback_data=AdminMenuCallback(action="order_contact").pack())
    builder.button(text="📞 Контакты", callback_data=AdminMenuCallback(action="contacts").pack())
    builder.adjust(1)
    return builder.as_markup()


def admin_categories_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Добавить категорию",
        callback_data=AdminCategoryCallback(action="add").pack(),
    )
    for cat in categories:
        builder.button(
            text=f"{cat.title} (sort: {cat.sort_order})",
            callback_data=AdminCategoryCallback(action="view", category_id=cat.id).pack(),
        )
    builder.button(
        text="🔙 Назад",
        callback_data=AdminMenuCallback(action="back").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_category_view_keyboard(category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔢 Изменить sort",
        callback_data=AdminCategoryCallback(action="sort", category_id=category_id).pack(),
    )
    builder.button(
        text="🗑 Удалить",
        callback_data=AdminCategoryCallback(action="delete", category_id=category_id).pack(),
    )
    builder.button(
        text="🔙 К списку",
        callback_data=AdminCategoryCallback(action="list").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_category_delete_confirm_keyboard(category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Да, удалить",
        callback_data=AdminConfirmCallback(
            action="delete_category", entity_id=category_id
        ).pack(),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=AdminCategoryCallback(action="view", category_id=category_id).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_products_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Добавить товар",
        callback_data=AdminProductAddCallback(action="start").pack(),
    )
    builder.button(
        text="📋 Список товаров",
        callback_data=AdminMenuCallback(action="product_list").pack(),
    )
    builder.button(
        text="🔙 Назад",
        callback_data=AdminMenuCallback(action="back").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_pick_category_keyboard(
    categories: list[Category],
    prefix: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        if prefix == "add_product":
            cb = AdminProductAddCallback(action="category", category_id=cat.id).pack()
        else:
            cb = AdminProductListCallback(category_id=cat.id, page=0).pack()
        builder.button(text=cat.title, callback_data=cb)
    builder.button(
        text="❌ Отмена",
        callback_data=AdminMenuCallback(action="products").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_product_list_keyboard(
    products: list[Product],
    category_id: int,
    page: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * PRODUCTS_PER_PAGE
    chunk = products[start : start + PRODUCTS_PER_PAGE]

    for p in chunk:
        builder.button(
            text=f"{p.title} — {p.price}",
            callback_data=AdminProductCallback(action="view", product_id=p.id).pack(),
        )

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                text="◀",
                callback_data=AdminProductListCallback(
                    category_id=category_id, page=page - 1
                ).pack(),
            )
        )
    if start + PRODUCTS_PER_PAGE < len(products):
        nav.append(
            InlineKeyboardButton(
                text="▶",
                callback_data=AdminProductListCallback(
                    category_id=category_id, page=page + 1
                ).pack(),
            )
        )
    if nav:
        builder.row(*nav)

    builder.button(
        text="🔙 К товарам",
        callback_data=AdminMenuCallback(action="products").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_product_view_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✏️ Редактировать",
        callback_data=AdminProductCallback(action="edit_menu", product_id=product_id).pack(),
    )
    builder.button(
        text="🗑 Удалить",
        callback_data=AdminProductCallback(action="delete", product_id=product_id).pack(),
    )
    builder.button(
        text="🔙 Назад",
        callback_data=AdminProductCallback(action="list_back", product_id=product_id).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_product_edit_menu_keyboard(product_id: int) -> InlineKeyboardMarkup:
    fields = [
        ("📷 Фото", "photos"),
        ("📁 Категория", "category"),
        ("📌 Название", "title"),
        ("📄 Описание", "description"),
        ("💰 Цена", "price"),
        ("🔢 Sort", "sort"),
    ]
    builder = InlineKeyboardBuilder()
    for label, field in fields:
        builder.button(
            text=label,
            callback_data=AdminProductEditCallback(field=field, product_id=product_id).pack(),
        )
    builder.button(
        text="🔙 К товару",
        callback_data=AdminProductCallback(action="view", product_id=product_id).pack(),
    )
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def admin_product_delete_confirm_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Да, удалить",
        callback_data=AdminConfirmCallback(
            action="delete_product", entity_id=product_id
        ).pack(),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=AdminProductCallback(action="view", product_id=product_id).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_add_product_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Сохранить",
        callback_data=AdminProductAddCallback(action="confirm").pack(),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=AdminProductAddCallback(action="cancel").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_add_product_photos_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Готово",
        callback_data=AdminProductAddCallback(action="photos_done").pack(),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=AdminProductAddCallback(action="cancel").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_product_photos_keyboard(
    product_id: int,
    photos: list[ProductPhoto],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Добавить фото",
        callback_data=AdminProductPhotoCallback(action="add", product_id=product_id).pack(),
    )
    for idx, photo in enumerate(photos, start=1):
        builder.button(
            text=f"🗑 Фото {idx}",
            callback_data=AdminProductPhotoCallback(
                action="delete",
                product_id=product_id,
                photo_id=photo.id,
            ).pack(),
        )
    builder.button(
        text="🔙 К товару",
        callback_data=AdminProductCallback(action="view", product_id=product_id).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_product_photo_delete_confirm_keyboard(
    product_id: int,
    photo_row_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Да, удалить",
        callback_data=AdminConfirmCallback(
            action="delete_product_photo",
            entity_id=photo_row_id,
        ).pack(),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=AdminProductPhotoCallback(
            action="list",
            product_id=product_id,
        ).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Отмена",
        callback_data=AdminMenuCallback(action="back").pack(),
    )
    return builder.as_markup()
