from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import AdminMenuCallback
from bot.keyboards.admin import (
    admin_categories_keyboard,
    admin_main_keyboard,
    admin_pick_category_keyboard,
    admin_products_menu_keyboard,
)
from bot.middlewares import AdminOnlyMiddleware
from bot.states import EditContactsStates, EditMenuTextStates
from bot.db import queries

router = Router()
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.ADMIN_WELCOME, reply_markup=admin_main_keyboard())


@router.callback_query(AdminMenuCallback.filter(F.action == "back"))
async def admin_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            texts.ADMIN_WELCOME,
            reply_markup=admin_main_keyboard(),
        )


@router.callback_query(AdminMenuCallback.filter(F.action == "categories"))
async def admin_categories(callback: CallbackQuery) -> None:
    categories = await queries.list_categories()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "📂 Категории",
            reply_markup=admin_categories_keyboard(categories),
        )


@router.callback_query(AdminMenuCallback.filter(F.action == "products"))
async def admin_products(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "📦 Товары",
            reply_markup=admin_products_menu_keyboard(),
        )


@router.callback_query(AdminMenuCallback.filter(F.action == "product_list"))
async def admin_product_list_pick_category(callback: CallbackQuery) -> None:
    categories = await queries.list_categories()
    await callback.answer()
    if not categories:
        if callback.message:
            await callback.message.edit_text(
                "Сначала добавьте категорию.",
                reply_markup=admin_products_menu_keyboard(),
            )
        return
    if callback.message:
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=admin_pick_category_keyboard(categories, prefix="list"),
        )


@router.callback_query(AdminMenuCallback.filter(F.action == "contacts"))
async def admin_contacts_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EditContactsStates.text)
    await callback.answer()
    if callback.message:
        current = await queries.get_setting("contacts")
        await callback.message.answer(
            f"{texts.CONTACTS_EDIT_PROMPT}\n\nТекущий текст:\n{current or '—'}",
        )


@router.callback_query(AdminMenuCallback.filter(F.action == "menu_text"))
async def admin_menu_text_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EditMenuTextStates.text)
    await callback.answer()
    if callback.message:
        current = await queries.get_setting("menu_text")
        await callback.message.answer(
            f"{texts.MENU_TEXT_EDIT_PROMPT}\n\nТекущий текст:\n{current or '—'}",
        )
