from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import (
    BackToMenuCallback,
    CarouselCallback,
    CategoryCallback,
    MenuCallback,
    NoopCallback,
    OrderCallback,
)
from bot.config import settings
from bot.db.queries import Category


def main_menu_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=cat.title,
            callback_data=CategoryCallback(category_id=cat.id).pack(),
        )
    builder.button(
        text="Контакты",
        callback_data=MenuCallback(action="contacts").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def carousel_keyboard(
    category_id: int,
    index: int,
    total: int,
    product_id: int,
) -> InlineKeyboardMarkup:
    prev_index = (index - 1) % total if total else 0
    next_index = (index + 1) % total if total else 0
    position = f"{index + 1} / {total}" if total else "0 / 0"

    builder = InlineKeyboardBuilder()
    if total > 0:
        builder.row(
            InlineKeyboardButton(
                text="◀",
                callback_data=CarouselCallback(
                    category_id=category_id, index=prev_index
                ).pack(),
            ),
            InlineKeyboardButton(
                text=position,
                callback_data=NoopCallback().pack(),
            ),
            InlineKeyboardButton(
                text="▶",
                callback_data=CarouselCallback(
                    category_id=category_id, index=next_index
                ).pack(),
            ),
        )
    if product_id:
        builder.row(
            InlineKeyboardButton(
                text="🛍 Хочу заказать",
                callback_data=OrderCallback(product_id=product_id).pack(),
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="🔙 В главное меню",
            callback_data=BackToMenuCallback().pack(),
        )
    )
    return builder.as_markup()


def order_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад в каталог",
            callback_data=BackToMenuCallback().pack(),
        ),
        InlineKeyboardButton(
            text="💬 Написать сейчас",
            url=f"tg://user?id={settings.primary_admin_id}",
        ),
    )
    return builder.as_markup()


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
