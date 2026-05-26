from aiogram import Router

from bot.handlers import catalog, order, user_menu
from bot.handlers.admin import admin_router

user_router = Router()
user_router.include_router(user_menu.router)
user_router.include_router(catalog.router)
user_router.include_router(order.router)
