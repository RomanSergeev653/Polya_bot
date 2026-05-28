from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import CarouselCallback, CategoryCallback, NoopCallback
from bot.db import queries
from bot.keyboards.user import carousel_keyboard, main_menu_keyboard
from bot.utils.product_display import send_product_photos

router = Router()


async def show_carousel(
    message: Message,
    category_id: int,
    product_index: int,
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

    product_index = product_index % len(products)
    product = products[product_index]
    if not product.photos:
        await message.answer("У товара нет фото.")
        return

    keyboard = carousel_keyboard(
        category_id=category_id,
        product_index=product_index,
        products_total=len(products),
        product_id=product.id,
    )
    footer = f"Товар {product_index + 1} / {len(products)}"

    await send_product_photos(
        message,
        product,
        reply_markup=keyboard,
        album_footer=footer,
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

    await callback.answer()
    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await show_carousel(
            callback.message,
            callback_data.category_id,
            callback_data.product_index,
        )


@router.callback_query(NoopCallback.filter())
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()
