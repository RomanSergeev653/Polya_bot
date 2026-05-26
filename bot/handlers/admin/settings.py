from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import texts
from bot.db import queries
from bot.keyboards.admin import admin_main_keyboard
from bot.middlewares import AdminOnlyMiddleware
from bot.states import EditContactsStates

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
