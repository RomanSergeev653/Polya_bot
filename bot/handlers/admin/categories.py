import aiosqlite
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import AdminCategoryCallback, AdminConfirmCallback
from bot.db import queries
from bot.keyboards.admin import (
    admin_categories_keyboard,
    admin_category_delete_confirm_keyboard,
    admin_category_view_keyboard,
)
from bot.middlewares import AdminOnlyMiddleware
from bot.states import AddCategoryStates, EditCategorySortStates

router = Router()
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())


@router.callback_query(AdminCategoryCallback.filter(F.action == "list"))
async def list_categories(callback: CallbackQuery) -> None:
    categories = await queries.list_categories()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "📂 Категории",
            reply_markup=admin_categories_keyboard(categories),
        )


@router.callback_query(AdminCategoryCallback.filter(F.action == "add"))
async def add_category_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddCategoryStates.title)
    await callback.answer()
    if callback.message:
        await callback.message.answer(texts.CATEGORY_ADD_PROMPT)


@router.message(AddCategoryStates.title)
async def add_category_finish(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer(texts.INVALID_INPUT)
        return
    try:
        await queries.create_category(title)
    except aiosqlite.IntegrityError:
        await message.answer("Категория с таким названием уже существует.")
        return

    await state.clear()
    categories = await queries.list_categories()
    await message.answer(
        texts.CATEGORY_ADDED.format(title=title),
        reply_markup=admin_categories_keyboard(categories),
    )


@router.callback_query(AdminCategoryCallback.filter(F.action == "view"))
async def view_category(callback: CallbackQuery, callback_data: AdminCategoryCallback) -> None:
    category = await queries.get_category(callback_data.category_id)
    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return
    count = await queries.count_products_in_category(category.id)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"📂 {category.title}\n"
            f"🔢 sort_order: {category.sort_order}\n"
            f"📦 товаров: {count}",
            reply_markup=admin_category_view_keyboard(category.id),
        )


@router.callback_query(AdminCategoryCallback.filter(F.action == "sort"))
async def edit_category_sort_start(
    callback: CallbackQuery,
    callback_data: AdminCategoryCallback,
    state: FSMContext,
) -> None:
    await state.set_state(EditCategorySortStates.sort_order)
    await state.update_data(category_id=callback_data.category_id)
    await callback.answer()
    if callback.message:
        await callback.message.answer("Введите новый sort_order (целое число):")


@router.message(EditCategorySortStates.sort_order)
async def edit_category_sort_finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category_id = data.get("category_id")
    try:
        sort_order = int((message.text or "").strip())
    except ValueError:
        await message.answer(texts.INVALID_INPUT)
        return

    await queries.update_category_sort(category_id, sort_order)
    await state.clear()
    category = await queries.get_category(category_id)
    count = await queries.count_products_in_category(category_id)
    await message.answer(
        texts.PRODUCT_UPDATED,
    )
    if category:
        await message.answer(
            f"📂 {category.title}\n"
            f"🔢 sort_order: {category.sort_order}\n"
            f"📦 товаров: {count}",
            reply_markup=admin_category_view_keyboard(category.id),
        )


@router.callback_query(AdminCategoryCallback.filter(F.action == "delete"))
async def delete_category_ask(
    callback: CallbackQuery,
    callback_data: AdminCategoryCallback,
) -> None:
    category = await queries.get_category(callback_data.category_id)
    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return
    count = await queries.count_products_in_category(category.id)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            texts.CATEGORY_DELETE_CONFIRM.format(title=category.title, count=count),
            reply_markup=admin_category_delete_confirm_keyboard(category.id),
        )


@router.callback_query(AdminConfirmCallback.filter(F.action == "delete_category"))
async def delete_category_confirm(
    callback: CallbackQuery,
    callback_data: AdminConfirmCallback,
) -> None:
    await queries.delete_category(callback_data.entity_id)
    categories = await queries.list_categories()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            texts.CATEGORY_DELETED,
            reply_markup=admin_categories_keyboard(categories),
        )
