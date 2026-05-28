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
