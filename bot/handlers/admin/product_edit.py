from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import AdminProductCallback, AdminProductEditCallback
from bot.db import queries
from bot.keyboards.admin import (
    admin_pick_category_keyboard,
    admin_product_edit_menu_keyboard,
    admin_product_view_keyboard,
)
from bot.middlewares import AdminOnlyMiddleware
from bot.states import EditProductStates
from bot.utils import format_product_caption

router = Router()
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())

FIELD_DB_MAP = {
    "photo": "photo_id",
    "title": "title",
    "description": "description",
    "price": "price",
    "sort": "sort_order",
}

FIELD_PROMPTS = {
    "photo": texts.PRODUCT_ADD_PHOTO,
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
        F.field.in_(["photo", "title", "description", "price", "sort"])
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
        await callback.message.answer(FIELD_PROMPTS.get(callback_data.field, "Введите значение:"))


@router.message(EditProductStates.waiting_value, F.photo)
async def edit_product_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("field") != "photo":
        await message.answer("Ожидался другой тип ввода.")
        return
    photo_id = message.photo[-1].file_id
    await queries.update_product_field(data["product_id"], "photo_id", photo_id)
    await state.clear()
    await _reply_updated_product_message(message, data["product_id"])


@router.message(EditProductStates.waiting_value)
async def edit_product_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data.get("field")
    product_id = data.get("product_id")
    value = (message.text or "").strip()

    if field == "photo":
        await message.answer("Отправьте фото.")
        return

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
    if product and callback.message:
        await callback.message.answer_photo(
            photo=product.photo_id,
            caption=format_product_caption(product),
            parse_mode="HTML",
            reply_markup=admin_product_view_keyboard(product.id),
        )


async def _reply_updated_product_message(message: Message, product_id: int) -> None:
    product = await queries.get_product(product_id)
    await message.answer(texts.PRODUCT_UPDATED)
    if product:
        await message.answer_photo(
            photo=product.photo_id,
            caption=format_product_caption(product),
            parse_mode="HTML",
            reply_markup=admin_product_view_keyboard(product.id),
        )
