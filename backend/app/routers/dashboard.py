from fastapi import APIRouter, Query
from app.services import ftl_db

router = APIRouter(prefix="/api/stats", tags=["dashboard"])


@router.get("/summary")
async def summary(hours: int = Query(24, ge=1, le=720)):
    return await ftl_db.get_summary(hours)


@router.get("/top-domains")
async def top_domains(
    limit: int = Query(10, ge=1, le=100),
    hours: int = Query(24, ge=1, le=720),
):
    return await ftl_db.get_top_domains(hours, limit)


@router.get("/top-blocked")
async def top_blocked(
    limit: int = Query(10, ge=1, le=100),
    hours: int = Query(24, ge=1, le=720),
):
    return await ftl_db.get_top_blocked(hours, limit)


@router.get("/over-time")
async def over_time(hours: int = Query(24, ge=1, le=720)):
    return await ftl_db.get_over_time(hours)


@router.get("/hourly-pattern")
async def hourly_pattern(days: int = Query(7, ge=1, le=30)):
    return await ftl_db.get_hourly_pattern(days)


@router.get("/blocklist-effectiveness")
async def blocklist_effectiveness():
    return await ftl_db.get_blocklist_effectiveness()
