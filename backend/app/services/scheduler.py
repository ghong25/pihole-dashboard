from __future__ import annotations

import asyncio
import time
import uuid
from app.services import device_db, pihole

# In-memory tracking of active timed blocks
_active_blocks: dict[str, dict] = {}
_task: asyncio.Task | None = None


async def init():
    """Load persisted timed blocks and start the checker task."""
    blocks = await device_db.get_active_timed_blocks()
    now = int(time.time())
    for b in blocks:
        if b["expires_at"] > now:
            _active_blocks[b["id"]] = b
        else:
            # Expired while app was down — clean up
            await _expire_block(b)

    global _task
    _task = asyncio.create_task(_check_loop())


async def shutdown():
    global _task
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None


async def _expire_block(block: dict):
    """Remove a domain from the blacklist and deactivate the record."""
    await pihole.remove_wildcard(block["domain"])
    await device_db.deactivate_timed_block(block["id"])
    _active_blocks.pop(block["id"], None)


async def _check_loop():
    while True:
        await asyncio.sleep(30)
        now = int(time.time())
        expired = [b for b in _active_blocks.values() if b["expires_at"] <= now]
        for b in expired:
            await _expire_block(b)


async def create_timed_block(domain: str, duration_minutes: int) -> dict:
    now = int(time.time())
    block_id = str(uuid.uuid4())
    expires_at = now + duration_minutes * 60
    comment = f"timed-block {block_id} expires {expires_at}"

    await pihole.add_wildcard(domain, comment=comment)
    await device_db.add_timed_block(block_id, domain, now, expires_at)

    block = {
        "id": block_id,
        "domain": domain,
        "created_at": now,
        "expires_at": expires_at,
    }
    _active_blocks[block_id] = block
    return block


async def cancel_timed_block(block_id: str) -> bool:
    block = _active_blocks.get(block_id)
    if not block:
        return False
    await _expire_block(block)
    return True


def get_active_blocks() -> list[dict]:
    now = int(time.time())
    result = []
    for b in _active_blocks.values():
        remaining = max(0, b["expires_at"] - now)
        result.append({**b, "remaining_seconds": remaining})
    return result
