from aiogram import Router
from aiogram.types import CallbackQuery

from bot import texts
from bot.callbacks import OrderCallback
from bot.db import queries
from bot.keyboards.user import order_keyboard

router = Router()


@router.callback_query(OrderCallback.filter())
async def want_to_order(callback: CallbackQuery, callback_data: OrderCallback) -> None:
    product = await queries.get_product(callback_data.product_id)
    await callback.answer()

    extra = ""
    if product:
        extra = f"\n\n📌 <b>{product.title}</b>\n💰 {product.price}"

    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await callback.message.answer(
            texts.ORDER_INSTRUCTION + extra,
            parse_mode="HTML",
            reply_markup=order_keyboard(),
        )
