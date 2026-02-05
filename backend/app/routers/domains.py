from __future__ import annotations

from fastapi import APIRouter, Query, HTTPException
from app.models import AddDomainRequest, ToggleDomainRequest, DOMAIN_PRESETS
from app.services import gravity_db, pihole

router = APIRouter(prefix="/api/domains", tags=["domains"])


@router.get("")
async def list_domains(type: str | None = Query(None)):
    return await gravity_db.get_domains(type)


@router.post("")
async def add_domain(req: AddDomainRequest):
    if req.type == "blacklist":
        code, out, err = await pihole.add_blacklist(req.domain, req.comment)
    elif req.type == "whitelist":
        code, out, err = await pihole.add_whitelist(req.domain)
    elif req.type == "regex_black":
        code, out, err = await pihole.add_regex_black(req.domain, req.comment)
    elif req.type == "wildcard":
        code, out, err = await pihole.add_wildcard(req.domain, req.comment)
    else:
        raise HTTPException(400, f"Unknown domain type: {req.type}")

    if code != 0:
        raise HTTPException(500, f"pihole command failed: {err or out}")

    return {"status": "ok", "output": out}


@router.delete("/{domain_id}")
async def delete_domain(domain_id: int):
    # Look up the domain to determine its type
    domains = await gravity_db.get_domains()
    target = None
    for d in domains:
        if d["id"] == domain_id:
            target = d
            break

    if not target:
        raise HTTPException(404, "Domain not found")

    type_code = target["type"]
    domain = target["domain"]

    if type_code == 1:  # blacklist
        code, out, err = await pihole.remove_blacklist(domain)
    elif type_code == 0:  # whitelist
        code, out, err = await pihole.remove_whitelist(domain)
    elif type_code == 3:  # regex black
        code, out, err = await pihole.remove_regex_black(domain)
    else:
        raise HTTPException(400, f"Unsupported domain type code: {type_code}")

    if code != 0:
        raise HTTPException(500, f"pihole command failed: {err or out}")

    return {"status": "ok"}


@router.patch("/{domain_id}")
async def toggle_domain(domain_id: int, req: ToggleDomainRequest):
    await gravity_db.toggle_domain(domain_id, req.enabled)
    await pihole.reload_lists()
    return {"status": "ok", "enabled": req.enabled}


@router.get("/presets")
async def get_presets():
    return DOMAIN_PRESETS
