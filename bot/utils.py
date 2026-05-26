from bot.db.queries import Product


def format_product_caption(product: Product) -> str:
    return (
        f"<b>{product.title}</b>\n"
        f"💰 {product.price}\n\n"
        f"{product.description}"
    )
