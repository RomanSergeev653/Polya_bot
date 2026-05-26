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
        await _seed_settings(db)


async def _seed_settings(db: aiosqlite.Connection) -> None:
    from bot.texts import CONTACTS_DEFAULT

    await db.execute("PRAGMA foreign_keys = ON")
    cursor = await db.execute(
        "SELECT value FROM settings WHERE key = ?",
        ("contacts",),
    )
    row = await cursor.fetchone()
    if row is None:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("contacts", CONTACTS_DEFAULT),
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
