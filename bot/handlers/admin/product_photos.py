from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import AdminConfirmCallback, AdminProductPhotoCallback
from bot.db import queries
from bot.keyboards.admin import (
    admin_product_photo_delete_confirm_keyboard,
    admin_product_photos_keyboard,
)
from bot.middlewares import AdminOnlyMiddleware
from bot.states import AddProductPhotoStates

router = Router()
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())


async def show_product_photos_menu(callback: CallbackQuery, product_id: int) -> None:
    product = await queries.get_product(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    photos = await queries.list_product_photos(product_id)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.PRODUCT_PHOTOS_TITLE.format(
                title=product.title,
                count=len(photos),
            ),
            reply_markup=admin_product_photos_keyboard(product_id, photos),
        )


@router.callback_query(AdminProductPhotoCallback.filter(F.action == "list"))
async def product_photos_list(
    callback: CallbackQuery,
    callback_data: AdminProductPhotoCallback,
) -> None:
    await show_product_photos_menu(callback, callback_data.product_id)


@router.callback_query(AdminProductPhotoCallback.filter(F.action == "add"))
async def product_photo_add_start(
    callback: CallbackQuery,
    callback_data: AdminProductPhotoCallback,
    state: FSMContext,
) -> None:
    await state.set_state(AddProductPhotoStates.waiting_photo)
    await state.update_data(product_id=callback_data.product_id)
    await callback.answer()
    if callback.message:
        await callback.message.answer(texts.PRODUCT_PHOTO_ADD_PROMPT)


@router.message(AddProductPhotoStates.waiting_photo, F.photo)
async def product_photo_add_finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    product_id = data.get("product_id")
    photo_id = message.photo[-1].file_id
    await queries.add_product_photo(product_id, photo_id)
    await state.clear()

    photos = await queries.list_product_photos(product_id)
    product = await queries.get_product(product_id)
    title = product.title if product else "—"
    await message.answer(texts.PRODUCT_PHOTO_ADDED)
    await message.answer(
        texts.PRODUCT_PHOTOS_TITLE.format(title=title, count=len(photos)),
        reply_markup=admin_product_photos_keyboard(product_id, photos),
    )


@router.message(AddProductPhotoStates.waiting_photo)
async def product_photo_add_invalid(message: Message) -> None:
    await message.answer("Отправьте фото.")


@router.callback_query(AdminProductPhotoCallback.filter(F.action == "delete"))
async def product_photo_delete_ask(
    callback: CallbackQuery,
    callback_data: AdminProductPhotoCallback,
) -> None:
    photo = await queries.get_product_photo(callback_data.photo_id)
    if not photo:
        await callback.answer("Фото не найдено", show_alert=True)
        return

    product = await queries.get_product(callback_data.product_id)
    if product and len(product.photos) <= 1:
        await callback.answer(texts.PRODUCT_PHOTO_DELETE_BLOCKED, show_alert=True)
        return

    await callback.answer()
    if callback.message:
        await callback.message.answer_photo(
            photo=photo.photo_id,
            caption=texts.PRODUCT_PHOTO_DELETE_CONFIRM,
            reply_markup=admin_product_photo_delete_confirm_keyboard(
                callback_data.product_id,
                photo.id,
            ),
        )


@router.callback_query(AdminConfirmCallback.filter(F.action == "delete_product_photo"))
async def product_photo_delete_confirm(
    callback: CallbackQuery,
    callback_data: AdminConfirmCallback,
) -> None:
    photo = await queries.get_product_photo(callback_data.entity_id)
    if not photo:
        await callback.answer("Фото не найдено", show_alert=True)
        return

    deleted = await queries.delete_product_photo(callback_data.entity_id)
    if not deleted:
        await callback.answer(texts.PRODUCT_PHOTO_DELETE_BLOCKED, show_alert=True)
        return

    photos = await queries.list_product_photos(photo.product_id)
    product = await queries.get_product(photo.product_id)
    await callback.answer(texts.PRODUCT_PHOTO_DELETED)
    if callback.message and product:
        await callback.message.answer(
            texts.PRODUCT_PHOTOS_TITLE.format(
                title=product.title,
                count=len(photos),
            ),
            reply_markup=admin_product_photos_keyboard(photo.product_id, photos),
        )
