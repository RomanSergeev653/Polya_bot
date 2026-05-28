from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import aiosqlite

from bot.config import DATA_DIR, DB_PATH

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


async def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.executescript(schema)
        await db.commit()
        await _migrate_legacy_photos(db)
        await _seed_settings(db)


async def _migrate_legacy_photos(db: aiosqlite.Connection) -> None:
    await db.execute("PRAGMA foreign_keys = ON")
    cursor = await db.execute("PRAGMA table_info(products)")
    columns = {row[1] for row in await cursor.fetchall()}
    if "photo_id" not in columns:
        return

    cursor = await db.execute(
        """
        SELECT p.id, p.photo_id
        FROM products p
        WHERE p.photo_id IS NOT NULL AND TRIM(p.photo_id) != ''
          AND NOT EXISTS (
              SELECT 1 FROM product_photos pp WHERE pp.product_id = p.id
          )
        """
    )
    rows = await cursor.fetchall()
    for product_id, photo_id in rows:
        await db.execute(
            """
            INSERT INTO product_photos (product_id, photo_id, sort_order)
            VALUES (?, ?, 0)
            """,
            (product_id, photo_id),
        )
    await db.commit()


async def _seed_settings(db: aiosqlite.Connection) -> None:
    from bot.texts import CONTACTS_DEFAULT, WELCOME

    await db.execute("PRAGMA foreign_keys = ON")
    defaults = {
        "contacts": CONTACTS_DEFAULT,
        "menu_text": WELCOME,
    }
    for key, value in defaults.items():
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        )
        row = await cursor.fetchone()
        if row is None:
            await db.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
    await db.commit()


@asynccontextmanager
async def connect() -> AsyncIterator[aiosqlite.Connection]:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
    finally:
        await db.close()
