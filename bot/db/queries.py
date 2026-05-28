from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bot.db.database import connect


@dataclass
class Category:
    id: int
    title: str
    sort_order: int


@dataclass
class ProductPhoto:
    id: int
    product_id: int
    photo_id: str
    sort_order: int


@dataclass
class Product:
    id: int
    category_id: int
    title: str
    description: str
    price: str
    sort_order: int
    photos: list[ProductPhoto] = field(default_factory=list)

    @property
    def primary_photo_id(self) -> str | None:
        return self.photos[0].photo_id if self.photos else None


def _row_to_category(row: Any) -> Category:
    return Category(
        id=row["id"],
        title=row["title"],
        sort_order=row["sort_order"],
    )


def _row_to_product(row: Any) -> Product:
    return Product(
        id=row["id"],
        category_id=row["category_id"],
        title=row["title"],
        description=row["description"],
        price=row["price"],
        sort_order=row["sort_order"],
    )


def _row_to_photo(row: Any) -> ProductPhoto:
    return ProductPhoto(
        id=row["id"],
        product_id=row["product_id"],
        photo_id=row["photo_id"],
        sort_order=row["sort_order"],
    )


async def _load_photos_for_products(products: list[Product]) -> list[Product]:
    if not products:
        return products
    ids = [p.id for p in products]
    placeholders = ",".join("?" * len(ids))
    async with connect() as db:
        cursor = await db.execute(
            f"""
            SELECT id, product_id, photo_id, sort_order
            FROM product_photos
            WHERE product_id IN ({placeholders})
            ORDER BY product_id, sort_order, id
            """,
            ids,
        )
        rows = await cursor.fetchall()

    photos_by_product: dict[int, list[ProductPhoto]] = {p.id: [] for p in products}
    for row in rows:
        photo = _row_to_photo(row)
        photos_by_product[photo.product_id].append(photo)

    for product in products:
        product.photos = photos_by_product.get(product.id, [])
    return products


async def list_product_photos(product_id: int) -> list[ProductPhoto]:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT id, product_id, photo_id, sort_order
            FROM product_photos
            WHERE product_id = ?
            ORDER BY sort_order, id
            """,
            (product_id,),
        )
        rows = await cursor.fetchall()
    return [_row_to_photo(r) for r in rows]


# --- Categories ---


async def list_categories() -> list[Category]:
    async with connect() as db:
        cursor = await db.execute(
            "SELECT id, title, sort_order FROM categories ORDER BY sort_order, id"
        )
        rows = await cursor.fetchall()
    return [_row_to_category(r) for r in rows]


async def get_category(category_id: int) -> Category | None:
    async with connect() as db:
        cursor = await db.execute(
            "SELECT id, title, sort_order FROM categories WHERE id = ?",
            (category_id,),
        )
        row = await cursor.fetchone()
    return _row_to_category(row) if row else None


async def create_category(title: str, sort_order: int = 0) -> Category:
    async with connect() as db:
        cursor = await db.execute(
            "INSERT INTO categories (title, sort_order) VALUES (?, ?)",
            (title.strip(), sort_order),
        )
        await db.commit()
        category_id = cursor.lastrowid
    cat = await get_category(category_id)
    assert cat is not None
    return cat


async def update_category_sort(category_id: int, sort_order: int) -> None:
    async with connect() as db:
        await db.execute(
            "UPDATE categories SET sort_order = ? WHERE id = ?",
            (sort_order, category_id),
        )
        await db.commit()


async def delete_category(category_id: int) -> None:
    async with connect() as db:
        await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        await db.commit()


async def count_products_in_category(category_id: int) -> int:
    async with connect() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM products WHERE category_id = ?",
            (category_id,),
        )
        row = await cursor.fetchone()
    return int(row[0])


# --- Products ---


async def list_products_by_category(category_id: int) -> list[Product]:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT id, category_id, title, description, price, sort_order
            FROM products
            WHERE category_id = ?
            ORDER BY sort_order, id
            """,
            (category_id,),
        )
        rows = await cursor.fetchall()
    products = [_row_to_product(r) for r in rows]
    return await _load_photos_for_products(products)


async def get_product(product_id: int) -> Product | None:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT id, category_id, title, description, price, sort_order
            FROM products WHERE id = ?
            """,
            (product_id,),
        )
        row = await cursor.fetchone()
    if not row:
        return None
    products = await _load_photos_for_products([_row_to_product(row)])
    return products[0]


async def create_product(
    category_id: int,
    title: str,
    description: str,
    price: str,
    photo_ids: list[str],
    sort_order: int = 0,
) -> Product:
    if not photo_ids:
        raise ValueError("Product must have at least one photo")

    async with connect() as db:
        cursor = await db.execute("PRAGMA table_info(products)")
        columns = {row[1] for row in await cursor.fetchall()}

        if "photo_id" in columns:
            cursor = await db.execute(
                """
                INSERT INTO products
                    (category_id, title, description, price, photo_id, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    category_id,
                    title.strip(),
                    description.strip(),
                    price.strip(),
                    photo_ids[0],
                    sort_order,
                ),
            )
        else:
            cursor = await db.execute(
                """
                INSERT INTO products
                    (category_id, title, description, price, sort_order)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    category_id,
                    title.strip(),
                    description.strip(),
                    price.strip(),
                    sort_order,
                ),
            )
        product_id = cursor.lastrowid
        for idx, photo_id in enumerate(photo_ids):
            await db.execute(
                """
                INSERT INTO product_photos (product_id, photo_id, sort_order)
                VALUES (?, ?, ?)
                """,
                (product_id, photo_id, idx),
            )
        await db.commit()

    product = await get_product(product_id)
    assert product is not None
    return product


async def update_product_field(product_id: int, field: str, value: Any) -> None:
    allowed = {"category_id", "title", "description", "price", "sort_order"}
    if field not in allowed:
        raise ValueError(f"Invalid field: {field}")
    async with connect() as db:
        await db.execute(
            f"UPDATE products SET {field} = ? WHERE id = ?",
            (value, product_id),
        )
        await db.commit()


async def delete_product(product_id: int) -> None:
    async with connect() as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()


# --- Product photos ---


async def add_product_photo(
    product_id: int,
    photo_id: str,
    sort_order: int | None = None,
) -> ProductPhoto:
    async with connect() as db:
        if sort_order is None:
            cursor = await db.execute(
                """
                SELECT COALESCE(MAX(sort_order), -1) + 1
                FROM product_photos WHERE product_id = ?
                """,
                (product_id,),
            )
            row = await cursor.fetchone()
            sort_order = int(row[0])

        cursor = await db.execute(
            """
            INSERT INTO product_photos (product_id, photo_id, sort_order)
            VALUES (?, ?, ?)
            """,
            (product_id, photo_id, sort_order),
        )
        await db.commit()
        photo_row_id = cursor.lastrowid

    photos = await list_product_photos(product_id)
    for photo in photos:
        if photo.id == photo_row_id:
            return photo
    raise RuntimeError("Failed to load created photo")


async def delete_product_photo(photo_row_id: int) -> bool:
    async with connect() as db:
        cursor = await db.execute(
            "SELECT product_id FROM product_photos WHERE id = ?",
            (photo_row_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return False
        product_id = row["product_id"]

        cursor = await db.execute(
            "SELECT COUNT(*) FROM product_photos WHERE product_id = ?",
            (product_id,),
        )
        count_row = await cursor.fetchone()
        if int(count_row[0]) <= 1:
            return False

        await db.execute("DELETE FROM product_photos WHERE id = ?", (photo_row_id,))
        await db.commit()
    return True


async def get_product_photo(photo_row_id: int) -> ProductPhoto | None:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT id, product_id, photo_id, sort_order
            FROM product_photos WHERE id = ?
            """,
            (photo_row_id,),
        )
        row = await cursor.fetchone()
    return _row_to_photo(row) if row else None


# --- Settings ---


async def get_setting(key: str) -> str | None:
    async with connect() as db:
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        )
        row = await cursor.fetchone()
    return row["value"] if row else None


async def set_setting(key: str, value: str) -> None:
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        await db.commit()
