from aiogram.types import InputMediaPhoto, Message

from bot.db.queries import Product


def format_product_caption(product: Product) -> str:
    return (
        f"<b>{product.title}</b>\n"
        f"💰 {product.price}\n\n"
        f"{product.description}"
    )


def get_photo_at(product: Product, photo_index: int) -> str | None:
    if not product.photos:
        return None
    index = photo_index % len(product.photos)
    return product.photos[index].photo_id


async def send_product_photos(
    target: Message,
    product: Product,
    *,
    caption: str | None = None,
    parse_mode: str = "HTML",
    reply_markup=None,
    album_footer: str | None = None,
) -> None:
    caption = caption or format_product_caption(product)
    photos = product.photos

    if not photos:
        await target.answer("У товара нет фото.")
        return

    if len(photos) == 1:
        await target.answer_photo(
            photo=photos[0].photo_id,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
        return

    media = [
        InputMediaPhoto(
            media=photo.photo_id,
            caption=caption if index == 0 else None,
            parse_mode=parse_mode if index == 0 else None,
        )
        for index, photo in enumerate(photos)
    ]
    await target.answer_media_group(media)

    footer = album_footer or f"📷 {len(photos)} фото"
    await target.answer(footer, reply_markup=reply_markup)
