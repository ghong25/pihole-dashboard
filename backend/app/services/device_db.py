from __future__ import annotations

import aiosqlite
from app.config import settings

_initialized = False


async def init_db():
    global _initialized
    if _initialized:
        return
    async with aiosqlite.connect(settings.dashboard_db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS device_nicknames (
                mac TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                icon TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS timed_blocks (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                active BOOLEAN NOT NULL DEFAULT 1
            )
            """
        )
        await db.commit()
    _initialized = True


async def get_nicknames() -> dict[str, dict]:
    await init_db()
    async with aiosqlite.connect(settings.dashboard_db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT mac, nickname, icon FROM device_nicknames") as c:
            rows = await c.fetchall()
            return {r["mac"]: {"nickname": r["nickname"], "icon": r["icon"]} for r in rows}


async def set_nickname(mac: str, nickname: str, icon: str | None = None):
    await init_db()
    async with aiosqlite.connect(settings.dashboard_db_path) as db:
        await db.execute(
            """
            INSERT INTO device_nicknames (mac, nickname, icon)
            VALUES (?, ?, ?)
            ON CONFLICT(mac) DO UPDATE SET nickname = excluded.nickname, icon = excluded.icon
            """,
            (mac, nickname, icon),
        )
        await db.commit()


# Timed blocks persistence
async def get_active_timed_blocks() -> list[dict]:
    await init_db()
    async with aiosqlite.connect(settings.dashboard_db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, domain, created_at, expires_at FROM timed_blocks WHERE active = 1"
        ) as c:
            rows = await c.fetchall()
            return [dict(r) for r in rows]


async def add_timed_block(block_id: str, domain: str, created_at: int, expires_at: int):
    await init_db()
    async with aiosqlite.connect(settings.dashboard_db_path) as db:
        await db.execute(
            "INSERT INTO timed_blocks (id, domain, created_at, expires_at, active) VALUES (?, ?, ?, ?, 1)",
            (block_id, domain, created_at, expires_at),
        )
        await db.commit()


async def deactivate_timed_block(block_id: str):
    await init_db()
    async with aiosqlite.connect(settings.dashboard_db_path) as db:
        await db.execute(
            "UPDATE timed_blocks SET active = 0 WHERE id = ?", (block_id,)
        )
        await db.commit()
