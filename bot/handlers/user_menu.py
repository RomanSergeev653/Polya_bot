from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import BackToMenuCallback, MenuCallback
from bot.db import queries
from bot.keyboards.user import main_menu_keyboard

router = Router()


async def send_main_menu(target: Message) -> None:
    categories = await queries.list_categories()
    await target.answer(
        texts.WELCOME,
        reply_markup=main_menu_keyboard(categories),
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await send_main_menu(message)


@router.callback_query(BackToMenuCallback.filter())
async def back_to_main_menu(callback: CallbackQuery) -> None:
    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await callback.answer()
    if callback.message:
        await send_main_menu(callback.message)


@router.callback_query(MenuCallback.filter(F.action == "contacts"))
async def show_contacts(callback: CallbackQuery) -> None:
    contacts = await queries.get_setting("contacts")
    text = contacts or texts.CONTACTS_DEFAULT
    await callback.answer()
    if callback.message:
        await callback.message.answer(text)
