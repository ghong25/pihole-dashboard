from __future__ import annotations

import aiosqlite
from app.config import settings


async def _fetch_all(query: str, params: tuple = ()) -> list[dict]:
    async with aiosqlite.connect(
        f"file:{settings.gravity_db_path}?mode=ro", uri=True
    ) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def _execute_rw(query: str, params: tuple = ()):
    """Write operation on gravity.db (only for toggling enabled status)."""
    async with aiosqlite.connect(settings.gravity_db_path) as db:
        await db.execute(query, params)
        await db.commit()


async def get_domains(domain_type: str | None = None) -> list[dict]:
    type_map = {
        "blacklist": 1,
        "whitelist": 0,
        "regex_black": 3,
        "regex_white": 2,
    }

    if domain_type and domain_type in type_map:
        return await _fetch_all(
            """
            SELECT id, type, domain, enabled, date_added, date_modified, comment
            FROM domainlist
            WHERE type = ?
            ORDER BY date_added DESC
            """,
            (type_map[domain_type],),
        )

    return await _fetch_all(
        """
        SELECT id, type, domain, enabled, date_added, date_modified, comment
        FROM domainlist
        ORDER BY type, date_added DESC
        """
    )


async def toggle_domain(domain_id: int, enabled: bool):
    await _execute_rw(
        "UPDATE domainlist SET enabled = ? WHERE id = ?",
        (1 if enabled else 0, domain_id),
    )


async def get_adlists() -> list[dict]:
    return await _fetch_all(
        """
        SELECT id, address, enabled, date_added, comment, number
        FROM adlist
        ORDER BY id
        """
    )
