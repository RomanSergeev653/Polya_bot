from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import texts
from bot.db import queries
from bot.keyboards.admin import admin_main_keyboard
from bot.middlewares import AdminOnlyMiddleware
from bot.states import EditContactsStates, EditMenuTextStates, EditOrderContactStates
from bot.utils import build_telegram_contact_url

router = Router()
router.message.middleware(AdminOnlyMiddleware())


@router.message(EditContactsStates.text)
async def save_contacts(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer(texts.INVALID_INPUT)
        return

    await queries.set_setting("contacts", text)
    await state.clear()
    await message.answer(
        texts.CONTACTS_UPDATED,
        reply_markup=admin_main_keyboard(),
    )


@router.message(EditMenuTextStates.text)
async def save_menu_text(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer(texts.INVALID_INPUT)
        return

    await queries.set_setting("menu_text", text)
    await state.clear()
    await message.answer(
        texts.MENU_TEXT_UPDATED,
        reply_markup=admin_main_keyboard(),
    )


@router.message(EditOrderContactStates.value)
async def save_order_contact(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not value:
        await message.answer(texts.INVALID_INPUT)
        return

    if not build_telegram_contact_url(value):
        await message.answer(texts.ORDER_CONTACT_INVALID)
        return

    await queries.set_setting("order_contact", value)
    await state.clear()
    await message.answer(
        texts.ORDER_CONTACT_UPDATED,
        reply_markup=admin_main_keyboard(),
    )
