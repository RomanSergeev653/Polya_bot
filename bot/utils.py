from bot.db.queries import Product


def format_product_caption(product: Product, photo_index: int = 0) -> str:
    photos_total = len(product.photos)
    photo_line = ""
    if photos_total > 1:
        photo_line = f"📸 {photo_index + 1} / {photos_total}\n\n"

    return (
        f"<b>{product.title}</b>\n"
        f"💰 {product.price}\n\n"
        f"{photo_line}"
        f"{product.description}"
    )


def get_photo_at(product: Product, photo_index: int) -> str | None:
    if not product.photos:
        return None
    index = photo_index % len(product.photos)
    return product.photos[index].photo_id
