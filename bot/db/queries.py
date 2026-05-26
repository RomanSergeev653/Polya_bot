from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bot.db.database import connect


@dataclass
class Category:
    id: int
    title: str
    sort_order: int


@dataclass
class Product:
    id: int
    category_id: int
    title: str
    description: str
    price: str
    photo_id: str
    sort_order: int


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
        photo_id=row["photo_id"],
        sort_order=row["sort_order"],
    )


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
            SELECT id, category_id, title, description, price, photo_id, sort_order
            FROM products
            WHERE category_id = ?
            ORDER BY sort_order, id
            """,
            (category_id,),
        )
        rows = await cursor.fetchall()
    return [_row_to_product(r) for r in rows]


async def get_product(product_id: int) -> Product | None:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT id, category_id, title, description, price, photo_id, sort_order
            FROM products WHERE id = ?
            """,
            (product_id,),
        )
        row = await cursor.fetchone()
    return _row_to_product(row) if row else None


async def create_product(
    category_id: int,
    title: str,
    description: str,
    price: str,
    photo_id: str,
    sort_order: int = 0,
) -> Product:
    async with connect() as db:
        cursor = await db.execute(
            """
            INSERT INTO products
                (category_id, title, description, price, photo_id, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (category_id, title.strip(), description.strip(), price.strip(), photo_id, sort_order),
        )
        await db.commit()
        product_id = cursor.lastrowid
    product = await get_product(product_id)
    assert product is not None
    return product


async def update_product_field(product_id: int, field: str, value: Any) -> None:
    allowed = {"category_id", "title", "description", "price", "photo_id", "sort_order"}
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
