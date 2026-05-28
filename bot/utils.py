import re

from aiogram.types import InputMediaPhoto, Message

from bot.config import settings
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


_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{5,32}$")


def build_telegram_contact_url(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    if value.startswith(("http://", "https://", "tg://")):
        return value
    if value.startswith("@"):
        username = value[1:].strip()
        if _USERNAME_RE.fullmatch(username):
            return f"https://t.me/{username}"
        return None
    if value.isdigit():
        return f"tg://user?id={value}"
    if _USERNAME_RE.fullmatch(value):
        return f"https://t.me/{value}"
    return None


async def get_order_contact_url() -> str:
    from bot.db import queries

    raw = await queries.get_setting("order_contact")
    if raw:
        url = build_telegram_contact_url(raw)
        if url:
            return url
    return f"tg://user?id={settings.primary_admin_id}"


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
