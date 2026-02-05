from __future__ import annotations

from fastapi import APIRouter, Query
from app.services import ftl_db

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
async def get_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    domain: str | None = Query(None),
    client: str | None = Query(None),
    status: str | None = Query(None),
    from_ts: int | None = Query(None, alias="from"),
    to_ts: int | None = Query(None, alias="to"),
):
    return await ftl_db.get_queries(
        page=page,
        per_page=per_page,
        domain=domain,
        client=client,
        status=status,
        from_ts=from_ts,
        to_ts=to_ts,
    )


@router.get("/search")
async def search_logs(
    q: str = Query(..., min_length=1),
    hours: int = Query(24, ge=1, le=168),
):
    return await ftl_db.search_queries(q, hours)
