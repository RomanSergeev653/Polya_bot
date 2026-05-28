from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.callbacks import (
    AdminConfirmCallback,
    AdminMenuCallback,
    AdminProductAddCallback,
    AdminProductCallback,
    AdminProductListCallback,
)
from bot.db import queries
from bot.keyboards.admin import (
    admin_add_product_confirm_keyboard,
    admin_add_product_photos_keyboard,
    admin_pick_category_keyboard,
    admin_product_delete_confirm_keyboard,
    admin_product_list_keyboard,
    admin_product_view_keyboard,
    admin_products_menu_keyboard,
)
from bot.middlewares import AdminOnlyMiddleware
from bot.states import AddProductStates
from bot.utils import format_product_caption, get_photo_at

router = Router()
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())


async def _append_photos(state: FSMContext, photo_ids: list[str]) -> list[str]:
    data = await state.get_data()
    current: list[str] = list(data.get("photo_ids", []))
    current.extend(photo_ids)
    await state.update_data(photo_ids=current)
    return current


@router.callback_query(AdminProductAddCallback.filter(F.action == "start"))
async def add_product_start(callback: CallbackQuery, state: FSMContext) -> None:
    categories = await queries.list_categories()
    await callback.answer()
    if not categories:
        if callback.message:
            await callback.message.answer("Сначала добавьте категорию.")
        return
    if callback.message:
        await callback.message.answer(
            texts.PRODUCT_ADD_CATEGORY,
            reply_markup=admin_pick_category_keyboard(categories, prefix="add_product"),
        )


@router.callback_query(AdminProductAddCallback.filter(F.action == "category"))
async def add_product_category(
    callback: CallbackQuery,
    callback_data: AdminProductAddCallback,
    state: FSMContext,
) -> None:
    await state.clear()
    await state.set_state(AddProductStates.photos)
    await state.update_data(category_id=callback_data.category_id, photo_ids=[])
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.PRODUCT_ADD_PHOTO,
            reply_markup=admin_add_product_photos_keyboard(),
        )


@router.message(AddProductStates.photos, F.photo)
async def add_product_photos(message: Message, state: FSMContext) -> None:
    current = await _append_photos(state, photo_ids)
    await message.answer(
        texts.PRODUCT_ADD_PHOTO_ADDED.format(count=len(current)),
        reply_markup=admin_add_product_photos_keyboard(),
    )


@router.message(AddProductStates.photos)
async def add_product_photos_invalid(message: Message) -> None:
    await message.answer(
        "Отправьте фото или нажмите «✅ Готово».",
        reply_markup=admin_add_product_photos_keyboard(),
    )


@router.callback_query(AdminProductAddCallback.filter(F.action == "photos_done"))
async def add_product_photos_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    photo_ids: list[str] = data.get("photo_ids", [])
    if not photo_ids:
        await callback.answer(texts.PRODUCT_ADD_PHOTO_REQUIRED, show_alert=True)
        return

    await state.set_state(AddProductStates.title)
    await callback.answer()
    if callback.message:
        await callback.message.answer(texts.PRODUCT_ADD_TITLE)


@router.message(AddProductStates.title)
async def add_product_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer(texts.INVALID_INPUT)
        return
    await state.update_data(title=title)
    await state.set_state(AddProductStates.description)
    await message.answer(texts.PRODUCT_ADD_DESCRIPTION)


@router.message(AddProductStates.description)
async def add_product_description(message: Message, state: FSMContext) -> None:
    description = (message.text or "").strip()
    if not description:
        await message.answer(texts.INVALID_INPUT)
        return
    await state.update_data(description=description)
    await state.set_state(AddProductStates.price)
    await message.answer(texts.PRODUCT_ADD_PRICE)


@router.message(AddProductStates.price)
async def add_product_price(message: Message, state: FSMContext) -> None:
    price = (message.text or "").strip()
    if not price:
        await message.answer(texts.INVALID_INPUT)
        return
    await state.update_data(price=price)
    await state.set_state(AddProductStates.sort_order)
    await message.answer(texts.PRODUCT_ADD_SORT)


@router.message(AddProductStates.sort_order)
async def add_product_sort(message: Message, state: FSMContext) -> None:
    try:
        sort_order = int((message.text or "").strip())
    except ValueError:
        await message.answer(texts.INVALID_INPUT)
        return

    await state.update_data(sort_order=sort_order)
    data = await state.get_data()
    category = await queries.get_category(data["category_id"])
    category_title = category.title if category else "—"
    photo_ids: list[str] = data.get("photo_ids", [])
    preview_photo = photo_ids[0] if photo_ids else None

    await state.set_state(AddProductStates.confirm)
    caption = texts.PRODUCT_ADD_CONFIRM.format(
        category=category_title,
        title=data["title"],
        price=data["price"],
        sort_order=sort_order,
        description=data["description"],
    )
    caption += f"\n\n📷 Фото: {len(photo_ids)} шт."

    if preview_photo:
        await message.answer_photo(
            photo=preview_photo,
            caption=caption,
            reply_markup=admin_add_product_confirm_keyboard(),
        )
    else:
        await message.answer(
            caption,
            reply_markup=admin_add_product_confirm_keyboard(),
        )


@router.callback_query(AdminProductAddCallback.filter(F.action == "confirm"))
async def add_product_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    required = (
        "category_id",
        "photo_ids",
        "title",
        "description",
        "price",
        "sort_order",
    )
    if not all(k in data for k in required):
        await callback.answer("Данные неполные", show_alert=True)
        return

    photo_ids: list[str] = data.get("photo_ids", [])
    if not photo_ids:
        await callback.answer(texts.PRODUCT_ADD_PHOTO_REQUIRED, show_alert=True)
        return

    await queries.create_product(
        category_id=data["category_id"],
        title=data["title"],
        description=data["description"],
        price=data["price"],
        photo_ids=photo_ids,
        sort_order=data["sort_order"],
    )
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(texts.PRODUCT_ADDED)
        await callback.message.answer(
            "📦 Товары",
            reply_markup=admin_products_menu_keyboard(),
        )


@router.callback_query(AdminProductAddCallback.filter(F.action == "cancel"))
async def add_product_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer(texts.CANCELLED)
    if callback.message:
        await callback.message.answer(
            "📦 Товары",
            reply_markup=admin_products_menu_keyboard(),
        )


@router.callback_query(AdminProductListCallback.filter())
async def admin_products_in_category(
    callback: CallbackQuery,
    callback_data: AdminProductListCallback,
) -> None:
    products = await queries.list_products_by_category(callback_data.category_id)
    category = await queries.get_category(callback_data.category_id)
    title = category.title if category else "Категория"
    await callback.answer()
    if callback.message:
        if not products:
            await callback.message.edit_text(
                f"В «{title}» пока нет товаров.",
                reply_markup=admin_products_menu_keyboard(),
            )
            return
        await callback.message.edit_text(
            f"📦 {title} — выберите товар:",
            reply_markup=admin_product_list_keyboard(
                products,
                callback_data.category_id,
                callback_data.page,
            ),
        )


@router.callback_query(AdminProductCallback.filter(F.action == "view"))
async def admin_product_view(
    callback: CallbackQuery,
    callback_data: AdminProductCallback,
) -> None:
    product = await queries.get_product(callback_data.product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    photo_id = get_photo_at(product, 0)
    if not photo_id:
        await callback.answer("У товара нет фото", show_alert=True)
        return

    caption = format_product_caption(product, 0)
    if len(product.photos) > 1:
        caption += f"\n\n📷 Всего фото: {len(product.photos)}"

    await callback.answer()
    if callback.message:
        await callback.message.answer_photo(
            photo=photo_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=admin_product_view_keyboard(product.id),
        )


@router.callback_query(AdminProductCallback.filter(F.action == "delete"))
async def admin_product_delete_ask(
    callback: CallbackQuery,
    callback_data: AdminProductCallback,
) -> None:
    product = await queries.get_product(callback_data.product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            f"Удалить «{product.title}»?",
            reply_markup=admin_product_delete_confirm_keyboard(product.id),
        )


@router.callback_query(AdminConfirmCallback.filter(F.action == "delete_product"))
async def admin_product_delete_confirm(
    callback: CallbackQuery,
    callback_data: AdminConfirmCallback,
) -> None:
    product = await queries.get_product(callback_data.entity_id)
    category_id = product.category_id if product else 0
    await queries.delete_product(callback_data.entity_id)
    await callback.answer(texts.PRODUCT_DELETED)
    if callback.message and category_id:
        products = await queries.list_products_by_category(category_id)
        category = await queries.get_category(category_id)
        title = category.title if category else ""
        if products:
            await callback.message.answer(
                f"📦 {title}:",
                reply_markup=admin_product_list_keyboard(products, category_id, 0),
            )
        else:
            await callback.message.answer(
                f"В «{title}» больше нет товаров.",
                reply_markup=admin_products_menu_keyboard(),
            )


@router.callback_query(AdminProductCallback.filter(F.action == "list_back"))
async def admin_product_list_back(
    callback: CallbackQuery,
    callback_data: AdminProductCallback,
) -> None:
    product = await queries.get_product(callback_data.product_id)
    if not product:
        await callback.answer()
        return
    products = await queries.list_products_by_category(product.category_id)
    category = await queries.get_category(product.category_id)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            f"📦 {category.title if category else ''}:",
            reply_markup=admin_product_list_keyboard(
                products, product.category_id, 0
            ),
        )
