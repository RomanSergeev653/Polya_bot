from aiogram import Router

from bot.handlers.admin import categories, menu, product_edit, products, settings

admin_router = Router()
admin_router.include_router(menu.router)
admin_router.include_router(categories.router)
admin_router.include_router(products.router)
admin_router.include_router(product_edit.router)
admin_router.include_router(settings.router)
