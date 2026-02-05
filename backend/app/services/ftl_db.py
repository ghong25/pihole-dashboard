from __future__ import annotations

import time
import aiosqlite
from app.config import settings

_cache: dict[str, tuple[float, any]] = {}
_max_ts: int | None = None
_max_ts_fetched: float = 0


def _get_cached(key: str, ttl: int):
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < ttl:
            return val
    return None


def _set_cached(key: str, val):
    _cache[key] = (time.time(), val)


async def _get_max_timestamp() -> int:
    """Get the latest query timestamp from FTL, cached for 30s.
    Falls back to system time if no data exists."""
    global _max_ts, _max_ts_fetched
    now = time.time()
    if _max_ts is not None and now - _max_ts_fetched < 30:
        return _max_ts
    row = await _fetch_one("SELECT MAX(timestamp) as max_ts FROM query_storage")
    if row and row["max_ts"]:
        _max_ts = int(row["max_ts"])
    else:
        _max_ts = int(now)
    _max_ts_fetched = now
    return _max_ts


async def _now() -> int:
    """Reference timestamp for queries — uses latest FTL data timestamp
    so queries work even when system clock is ahead of DB data."""
    return await _get_max_timestamp()


async def _fetch_all(query: str, params: tuple = ()) -> list[dict]:
    async with aiosqlite.connect(
        f"file:{settings.ftl_db_path}?mode=ro", uri=True
    ) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def _fetch_one(query: str, params: tuple = ()) -> dict | None:
    async with aiosqlite.connect(
        f"file:{settings.ftl_db_path}?mode=ro", uri=True
    ) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_summary(hours: int = 24) -> dict:
    cache_key = f"summary:{hours}"
    cached = _get_cached(cache_key, settings.stats_cache_ttl)
    if cached is not None:
        return cached

    since = (await _now()) - hours * 3600
    row = await _fetch_one(
        """
        SELECT
            COUNT(*) as total_queries,
            SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries,
            COUNT(DISTINCT domain) as unique_domains,
            COUNT(DISTINCT client) as unique_clients
        FROM queries
        WHERE timestamp > ?
        """,
        (since,),
    )
    if row and row["total_queries"] > 0:
        row["blocked_percentage"] = round(
            row["blocked_queries"] / row["total_queries"] * 100, 1
        )
    else:
        row = row or {}
        row["blocked_percentage"] = 0.0

    _set_cached(cache_key, row)
    return row


async def get_top_domains(hours: int = 24, limit: int = 10) -> list[dict]:
    cache_key = f"top_domains:{hours}:{limit}"
    cached = _get_cached(cache_key, settings.stats_cache_ttl)
    if cached is not None:
        return cached

    since = (await _now()) - hours * 3600
    rows = await _fetch_all(
        """
        SELECT domain, COUNT(*) as count
        FROM queries
        WHERE timestamp > ?
        GROUP BY domain
        ORDER BY count DESC
        LIMIT ?
        """,
        (since, limit),
    )
    _set_cached(cache_key, rows)
    return rows


async def get_top_blocked(hours: int = 24, limit: int = 10) -> list[dict]:
    cache_key = f"top_blocked:{hours}:{limit}"
    cached = _get_cached(cache_key, settings.stats_cache_ttl)
    if cached is not None:
        return cached

    since = (await _now()) - hours * 3600
    rows = await _fetch_all(
        """
        SELECT domain, COUNT(*) as count
        FROM queries
        WHERE timestamp > ? AND status IN (1,4,5,6,7,8,9,10,11)
        GROUP BY domain
        ORDER BY count DESC
        LIMIT ?
        """,
        (since, limit),
    )
    _set_cached(cache_key, rows)
    return rows


async def get_over_time(hours: int = 24) -> list[dict]:
    cache_key = f"over_time:{hours}"
    cached = _get_cached(cache_key, settings.stats_cache_ttl)
    if cached is not None:
        return cached

    since = (await _now()) - hours * 3600
    interval = 600  # 10-minute buckets
    rows = await _fetch_all(
        """
        SELECT
            (timestamp / ?) * ? as bucket,
            SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked,
            SUM(CASE WHEN status NOT IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as allowed
        FROM queries
        WHERE timestamp > ?
        GROUP BY bucket
        ORDER BY bucket
        """,
        (interval, interval, since),
    )
    _set_cached(cache_key, rows)
    return rows


async def get_hourly_pattern(days: int = 7) -> list[dict]:
    cache_key = f"hourly_pattern:{days}"
    cached = _get_cached(cache_key, settings.heavy_cache_ttl)
    if cached is not None:
        return cached

    since = (await _now()) - days * 86400
    rows = await _fetch_all(
        """
        SELECT
            CAST(strftime('%w', timestamp, 'unixepoch', 'localtime') AS INTEGER) as day_of_week,
            CAST(strftime('%H', timestamp, 'unixepoch', 'localtime') AS INTEGER) as hour,
            COUNT(*) as count
        FROM queries
        WHERE timestamp > ?
        GROUP BY day_of_week, hour
        ORDER BY day_of_week, hour
        """,
        (since,),
    )
    _set_cached(cache_key, rows)
    return rows


async def get_blocklist_effectiveness() -> list[dict]:
    cache_key = "blocklist_effectiveness"
    cached = _get_cached(cache_key, settings.heavy_cache_ttl)
    if cached is not None:
        return cached

    # This requires joining with gravity.db, so we query FTL for blocked domains
    # and then match against adlists. For simplicity, we get the top blocked
    # domains and their counts.
    since = (await _now()) - 86400
    rows = await _fetch_all(
        """
        SELECT
            COALESCE(additional_info, 'unknown') as source,
            COUNT(*) as count
        FROM queries
        WHERE timestamp > ? AND status IN (1,4,5,6,7,8,9,10,11)
            AND additional_info IS NOT NULL AND additional_info != ''
        GROUP BY source
        ORDER BY count DESC
        LIMIT 20
        """,
        (since,),
    )
    _set_cached(cache_key, rows)
    return rows


async def get_queries(
    page: int = 1,
    per_page: int = 50,
    domain: str | None = None,
    client: str | None = None,
    status: str | None = None,
    from_ts: int | None = None,
    to_ts: int | None = None,
) -> dict:
    now = await _now()
    if from_ts is None:
        from_ts = now - 86400
    if to_ts is None:
        to_ts = now

    conditions = ["timestamp >= ?", "timestamp <= ?"]
    params: list = [from_ts, to_ts]

    if domain:
        conditions.append("domain LIKE ?")
        params.append(f"%{domain}%")
    if client:
        conditions.append("client = ?")
        params.append(client)
    if status:
        status_map = {
            "blocked": "(1,4,5,6,7,8,9,10,11)",
            "allowed": "(2,3,12,13,14)",
            "cached": "(3,)",
        }
        if status in status_map:
            conditions.append(f"status IN {status_map[status]}")

    where = " AND ".join(conditions)
    offset = (page - 1) * per_page

    count_row = await _fetch_one(
        f"SELECT COUNT(*) as total FROM queries WHERE {where}", tuple(params)
    )
    total = count_row["total"] if count_row else 0

    rows = await _fetch_all(
        f"""
        SELECT id, timestamp, type, status, domain, client, forward, reply_type, reply_time, dnssec
        FROM queries
        WHERE {where}
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        """,
        tuple(params + [per_page, offset]),
    )

    return {
        "items": rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


async def search_queries(q: str, hours: int = 24, limit: int = 50) -> list[dict]:
    since = (await _now()) - hours * 3600
    return await _fetch_all(
        """
        SELECT id, timestamp, type, status, domain, client, forward
        FROM queries
        WHERE timestamp > ? AND domain LIKE ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (since, f"%{q}%", limit),
    )


# Device-specific queries
async def get_device_stats(ip: str, hours: int = 24) -> dict:
    since = (await _now()) - hours * 3600
    row = await _fetch_one(
        """
        SELECT
            COUNT(*) as total_queries,
            SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries,
            COUNT(DISTINCT domain) as unique_domains
        FROM queries
        WHERE timestamp > ? AND client = ?
        """,
        (since, ip),
    )
    if row and row["total_queries"] > 0:
        row["blocked_percentage"] = round(
            row["blocked_queries"] / row["total_queries"] * 100, 1
        )
    else:
        row = row or {}
        row["blocked_percentage"] = 0.0
    return row


async def get_device_activity(ip: str, hours: int = 24) -> list[dict]:
    since = (await _now()) - hours * 3600
    interval = 600
    return await _fetch_all(
        """
        SELECT
            (timestamp / ?) * ? as bucket,
            SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked,
            SUM(CASE WHEN status NOT IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as allowed
        FROM queries
        WHERE timestamp > ? AND client = ?
        GROUP BY bucket
        ORDER BY bucket
        """,
        (interval, interval, since, ip),
    )


async def get_device_top_domains(ip: str, limit: int = 10) -> list[dict]:
    since = (await _now()) - 86400
    return await _fetch_all(
        """
        SELECT domain, COUNT(*) as count
        FROM queries
        WHERE timestamp > ? AND client = ?
        GROUP BY domain
        ORDER BY count DESC
        LIMIT ?
        """,
        (since, ip, limit),
    )


async def get_device_top_blocked(ip: str, limit: int = 10) -> list[dict]:
    since = (await _now()) - 86400
    return await _fetch_all(
        """
        SELECT domain, COUNT(*) as count
        FROM queries
        WHERE timestamp > ? AND client = ? AND status IN (1,4,5,6,7,8,9,10,11)
        GROUP BY domain
        ORDER BY count DESC
        LIMIT ?
        """,
        (since, ip, limit),
    )


async def get_network_devices() -> list[dict]:
    """Get devices from Pi-hole's network tables."""
    return await _fetch_all(
        """
        SELECT
            n.id,
            n.hwaddr as mac,
            n.interface,
            n.firstSeen as first_seen,
            n.lastQuery as last_query,
            n.numQueries as num_queries,
            n.macVendor as vendor,
            na.ip,
            na.name as hostname
        FROM network n
        LEFT JOIN network_addresses na ON na.network_id = n.id
        WHERE n.hwaddr != '00:00:00:00:00:00'
        ORDER BY n.lastQuery DESC
        """
    )
