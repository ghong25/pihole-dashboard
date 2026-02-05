from fastapi import APIRouter, Query
from app.models import UpdateDeviceRequest
from app.services import ftl_db, device_db

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
async def list_devices():
    devices = await ftl_db.get_network_devices()
    nicknames = await device_db.get_nicknames()

    # Merge nickname data into device records
    for d in devices:
        mac = d.get("mac", "")
        if mac in nicknames:
            d["nickname"] = nicknames[mac]["nickname"]
            d["icon"] = nicknames[mac]["icon"]
        else:
            d["nickname"] = None
            d["icon"] = None

    return devices


@router.patch("/{mac:path}")
async def update_device(mac: str, req: UpdateDeviceRequest):
    await device_db.set_nickname(mac, req.nickname, req.icon)
    return {"mac": mac, "nickname": req.nickname, "icon": req.icon}


@router.get("/{mac:path}/stats")
async def device_stats(mac: str, hours: int = Query(24, ge=1, le=720)):
    # We need to find the IP for this MAC first
    devices = await ftl_db.get_network_devices()
    ip = None
    for d in devices:
        if d["mac"] == mac:
            ip = d.get("ip")
            break

    if not ip:
        return {"error": "Device not found", "total_queries": 0, "blocked_queries": 0, "blocked_percentage": 0}

    return await ftl_db.get_device_stats(ip, hours)


@router.get("/{mac:path}/activity")
async def device_activity(mac: str, hours: int = Query(24, ge=1, le=168)):
    devices = await ftl_db.get_network_devices()
    ip = None
    for d in devices:
        if d["mac"] == mac:
            ip = d.get("ip")
            break

    if not ip:
        return []

    return await ftl_db.get_device_activity(ip, hours)


@router.get("/{mac:path}/top-domains")
async def device_top_domains(mac: str, limit: int = Query(10, ge=1, le=100)):
    devices = await ftl_db.get_network_devices()
    ip = None
    for d in devices:
        if d["mac"] == mac:
            ip = d.get("ip")
            break

    if not ip:
        return []

    return await ftl_db.get_device_top_domains(ip, limit)


@router.get("/{mac:path}/top-blocked")
async def device_top_blocked(mac: str, limit: int = Query(10, ge=1, le=100)):
    devices = await ftl_db.get_network_devices()
    ip = None
    for d in devices:
        if d["mac"] == mac:
            ip = d.get("ip")
            break

    if not ip:
        return []

    return await ftl_db.get_device_top_blocked(ip, limit)
