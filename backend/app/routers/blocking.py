from fastapi import APIRouter, HTTPException
from app.models import TimedBlockRequest
from app.services import scheduler

router = APIRouter(prefix="/api/timed-blocks", tags=["timed-blocks"])


@router.get("")
async def list_timed_blocks():
    return scheduler.get_active_blocks()


@router.post("")
async def create_timed_block(req: TimedBlockRequest):
    results = []
    for domain in req.domains:
        block = await scheduler.create_timed_block(domain, req.duration_minutes)
        results.append(block)
    return results


@router.delete("/{block_id}")
async def cancel_timed_block(block_id: str):
    success = await scheduler.cancel_timed_block(block_id)
    if not success:
        raise HTTPException(404, "Timed block not found or already expired")
    return {"status": "ok"}
