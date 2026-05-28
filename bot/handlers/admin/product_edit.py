from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import AdminProductCallback, AdminProductEditCallback
from bot.db import queries
from bot.keyboards.admin import (
    admin_product_edit_menu_keyboard,
    admin_product_view_keyboard,
)
from bot.middlewares import AdminOnlyMiddleware
from bot.handlers.admin.product_photos import show_product_photos_menu
from bot.states import EditProductStates
from bot.utils.product_display import send_product_photos

router = Router()
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())

FIELD_DB_MAP = {
    "title": "title",
    "description": "description",
    "price": "price",
    "sort": "sort_order",
}

FIELD_PROMPTS = {
    "category": "Выберите новую категорию:",
    "title": texts.PRODUCT_ADD_TITLE,
    "description": texts.PRODUCT_ADD_DESCRIPTION,
    "price": texts.PRODUCT_ADD_PRICE,
    "sort": texts.PRODUCT_ADD_SORT,
}


@router.callback_query(AdminProductCallback.filter(F.action == "edit_menu"))
async def edit_product_menu(
    callback: CallbackQuery,
    callback_data: AdminProductCallback,
) -> None:
    product = await queries.get_product(callback_data.product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            f"Что изменить в «{product.title}»?",
            reply_markup=admin_product_edit_menu_keyboard(product.id),
        )


@router.callback_query(AdminProductEditCallback.filter(F.field == "photos"))
async def edit_product_photos_menu(
    callback: CallbackQuery,
    callback_data: AdminProductEditCallback,
) -> None:
    await show_product_photos_menu(callback, callback_data.product_id)


@router.callback_query(AdminProductEditCallback.filter(F.field == "category"))
async def edit_product_category_pick(
    callback: CallbackQuery,
    callback_data: AdminProductEditCallback,
) -> None:
    categories = await queries.list_categories()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            FIELD_PROMPTS["category"],
            reply_markup=_category_pick_for_edit(
                categories, callback_data.product_id
            ),
        )


def _category_pick_for_edit(categories, product_id: int):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    from bot.callbacks import AdminProductEditCallback

    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=cat.title,
            callback_data=AdminProductEditCallback(
                field=f"set_cat:{cat.id}",
                product_id=product_id,
            ).pack(),
        )
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(AdminProductEditCallback.filter(F.field.startswith("set_cat:")))
async def edit_product_category_apply(
    callback: CallbackQuery,
    callback_data: AdminProductEditCallback,
) -> None:
    category_id = int(callback_data.field.split(":", 1)[1])
    await queries.update_product_field(callback_data.product_id, "category_id", category_id)
    await _reply_updated_product(callback, callback_data.product_id)


@router.callback_query(
    AdminProductEditCallback.filter(
        F.field.in_(["title", "description", "price", "sort"])
    )
)
async def edit_product_field_start(
    callback: CallbackQuery,
    callback_data: AdminProductEditCallback,
    state: FSMContext,
) -> None:
    product = await queries.get_product(callback_data.product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    await state.set_state(EditProductStates.waiting_value)
    await state.update_data(
        product_id=callback_data.product_id,
        field=callback_data.field,
    )
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            FIELD_PROMPTS.get(callback_data.field, "Введите значение:")
        )


@router.message(EditProductStates.waiting_value)
async def edit_product_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data.get("field")
    product_id = data.get("product_id")
    value = (message.text or "").strip()

    if not value:
        await message.answer(texts.INVALID_INPUT)
        return

    if field == "sort":
        try:
            value = int(value)
        except ValueError:
            await message.answer(texts.INVALID_INPUT)
            return
        db_field = "sort_order"
    else:
        db_field = FIELD_DB_MAP.get(field, field)

    await queries.update_product_field(product_id, db_field, value)
    await state.clear()
    await _reply_updated_product_message(message, product_id)


async def _reply_updated_product(callback: CallbackQuery, product_id: int) -> None:
    await callback.answer(texts.PRODUCT_UPDATED)
    product = await queries.get_product(product_id)
    if not product or not callback.message:
        return
    await send_product_photos(
        callback.message,
        product,
        reply_markup=admin_product_view_keyboard(product.id),
    )


async def _reply_updated_product_message(message: Message, product_id: int) -> None:
    product = await queries.get_product(product_id)
    await message.answer(texts.PRODUCT_UPDATED)
    if not product:
        return
    await send_product_photos(
        message,
        product,
        reply_markup=admin_product_view_keyboard(product.id),
    )
