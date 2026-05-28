from aiogram import F, Router
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from bot import texts
from bot.callbacks import CarouselCallback, CategoryCallback, NoopCallback
from bot.db import queries
from bot.keyboards.user import carousel_keyboard, main_menu_keyboard
from bot.utils import format_product_caption, get_photo_at

router = Router()


def _normalize_indices(products: list, product_index: int, photo_index: int):
    product_index = product_index % len(products)
    product = products[product_index]
    photos_total = len(product.photos)
    if photos_total == 0:
        return product_index, 0, product, 0, None
    photo_index = photo_index % photos_total
    photo_id = get_photo_at(product, photo_index)
    return product_index, photo_index, product, photos_total, photo_id


async def show_carousel(
    message: Message,
    category_id: int,
    product_index: int,
    photo_index: int = 0,
) -> None:
    products = await queries.list_products_by_category(category_id)
    category = await queries.get_category(category_id)

    if not category:
        await message.answer("Категория не найдена.")
        return

    if not products:
        categories = await queries.list_categories()
        await message.answer(
            texts.EMPTY_CATEGORY,
            reply_markup=main_menu_keyboard(categories),
        )
        return

    product_index, photo_index, product, photos_total, photo_id = _normalize_indices(
        products, product_index, photo_index
    )
    if not photo_id:
        await message.answer("У товара нет фото.")
        return

    caption = format_product_caption(product, photo_index)
    keyboard = carousel_keyboard(
        category_id=category_id,
        product_index=product_index,
        products_total=len(products),
        product_id=product.id,
        photo_index=photo_index,
        photos_total=photos_total,
    )

    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(CategoryCallback.filter())
async def open_category(callback: CallbackQuery, callback_data: CategoryCallback) -> None:
    await callback.answer()
    if callback.message:
        await show_carousel(callback.message, callback_data.category_id, 0, 0)


@router.callback_query(CarouselCallback.filter())
async def carousel_navigate(
    callback: CallbackQuery,
    callback_data: CarouselCallback,
) -> None:
    products = await queries.list_products_by_category(callback_data.category_id)
    if not products:
        await callback.answer(texts.EMPTY_CATEGORY, show_alert=True)
        return

    product_index, photo_index, product, photos_total, photo_id = _normalize_indices(
        products,
        callback_data.product_index,
        callback_data.photo_index,
    )
    if not photo_id:
        await callback.answer("У товара нет фото.", show_alert=True)
        return

    caption = format_product_caption(product, photo_index)
    keyboard = carousel_keyboard(
        category_id=callback_data.category_id,
        product_index=product_index,
        products_total=len(products),
        product_id=product.id,
        photo_index=photo_index,
        photos_total=photos_total,
    )

    await callback.answer()
    if callback.message and callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=photo_id,
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=keyboard,
        )


@router.callback_query(NoopCallback.filter())
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()
