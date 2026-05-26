from aiogram import F, Router
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from bot import texts
from bot.callbacks import CarouselCallback, CategoryCallback, NoopCallback
from bot.db import queries
from bot.keyboards.user import carousel_keyboard, main_menu_keyboard
from bot.utils import format_product_caption

router = Router()


async def show_carousel(message: Message, category_id: int, index: int) -> None:
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

    index = index % len(products)
    product = products[index]
    caption = format_product_caption(product)
    keyboard = carousel_keyboard(
        category_id=category_id,
        index=index,
        total=len(products),
        product_id=product.id,
    )

    await message.answer_photo(
        photo=product.photo_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(CategoryCallback.filter())
async def open_category(callback: CallbackQuery, callback_data: CategoryCallback) -> None:
    await callback.answer()
    if callback.message:
        await show_carousel(callback.message, callback_data.category_id, 0)


@router.callback_query(CarouselCallback.filter())
async def carousel_navigate(
    callback: CallbackQuery,
    callback_data: CarouselCallback,
) -> None:
    products = await queries.list_products_by_category(callback_data.category_id)
    if not products:
        await callback.answer(texts.EMPTY_CATEGORY, show_alert=True)
        return

    index = callback_data.index % len(products)
    product = products[index]
    caption = format_product_caption(product)
    keyboard = carousel_keyboard(
        category_id=callback_data.category_id,
        index=index,
        total=len(products),
        product_id=product.id,
    )

    await callback.answer()
    if callback.message and callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=product.photo_id,
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=keyboard,
        )


@router.callback_query(NoopCallback.filter())
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()
