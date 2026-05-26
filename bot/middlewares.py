from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.config import settings
from bot.texts import ADMIN_ACCESS_DENIED


class AdminOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if not settings.is_admin(user_id):
            if isinstance(event, Message):
                await event.answer(ADMIN_ACCESS_DENIED)
            elif isinstance(event, CallbackQuery):
                await event.answer(ADMIN_ACCESS_DENIED, show_alert=True)
            return None

        return await handler(event, data)
