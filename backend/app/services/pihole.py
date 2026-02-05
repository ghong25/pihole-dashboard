from __future__ import annotations

import asyncio
import shlex
from app.config import settings


async def run_pihole(*args: str) -> tuple[int, str, str]:
    cmd_parts = []
    if settings.use_sudo:
        cmd_parts.append("sudo")
    cmd_parts.append(settings.pihole_command)
    cmd_parts.extend(args)

    cmd = " ".join(shlex.quote(p) for p in cmd_parts)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode().strip(), stderr.decode().strip()


# Pi-hole v5 CLI commands:
#   -b / blacklist      (v6 uses "deny")
#   -w / whitelist      (v6 uses "allow")
#   --regex             same in both
#   --wild / wildcard   same in both
#   -d flag for removal (not "--remove")
#   --comment "text"    same in both

async def add_blacklist(domain: str, comment: str | None = None):
    args = ["-b", domain]
    if comment:
        args.extend(["--comment", comment])
    return await run_pihole(*args)


async def remove_blacklist(domain: str):
    return await run_pihole("-b", "-d", domain)


async def add_whitelist(domain: str):
    return await run_pihole("-w", domain)


async def remove_whitelist(domain: str):
    return await run_pihole("-w", "-d", domain)


async def add_regex_black(pattern: str, comment: str | None = None):
    args = ["--regex", pattern]
    if comment:
        args.extend(["--comment", comment])
    return await run_pihole(*args)


async def remove_regex_black(pattern: str):
    return await run_pihole("--regex", "-d", pattern)


async def add_wildcard(domain: str, comment: str | None = None):
    args = ["--wild", domain]
    if comment:
        args.extend(["--comment", comment])
    return await run_pihole(*args)


async def remove_wildcard(domain: str):
    return await run_pihole("--wild", "-d", domain)


async def reload_lists():
    return await run_pihole("restartdns", "reload-lists")
