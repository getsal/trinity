"""Credential-scoped official Codex ChatGPT login storage.

The Codex CLI owns OAuth and refresh tokens. Trinity gives each account its own
private Docker volume, starts the official ``codex login --device-auth`` flow,
and mounts that writable state into only one Codex agent. One credential is
single-agent because a refreshable auth.json cannot safely be shared by
concurrent containers.
"""

from __future__ import annotations

import re
from typing import Any, Optional

import docker
from fastapi import HTTPException

from database import db
from services.docker_utils import (
    container_create,
    container_get,
    container_logs,
    container_reload,
    container_remove,
    container_start,
    containers_run,
    volume_create,
    volume_get,
    volume_remove,
)

CODEX_IMAGE = "trinity-agent-base:latest"
CODEX_HOME = "/home/developer/.codex"
_LOGIN_CONTAINER_PREFIX = "trinity-codex-login-"
_AUTH_VOLUME_PREFIX = "trinity-codex-auth-"
_URL_RE = re.compile(r"https://[^\s'\"]+")
_ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
_DEVICE_CODE_RE = re.compile(
    r"(?i:(?:one[- ]time|device)(?:[- ]authorization)?\s+code|code)\s*(?:is)?\s*[:=]?\s*([A-Z0-9]{4}-[A-Z0-9]{5}|[A-Z0-9]{8,})"
)
_HYPHENATED_DEVICE_CODE_RE = re.compile(r"\b[A-Z0-9]{4}-[A-Z0-9]{5}\b")
_RATE_LIMIT_RE = re.compile(r"(?:\b429\b|too many requests|rate limit(?:ed)?)", re.IGNORECASE)


def auth_volume_name(subscription_id: str) -> str:
    return f"{_AUTH_VOLUME_PREFIX}{subscription_id}"


def login_container_name(subscription_id: str) -> str:
    return f"{_LOGIN_CONTAINER_PREFIX}{subscription_id}"


def _extract_device_codes(output: str) -> list[str]:
    """Extract only the official short device code, never auth tokens or logs."""
    labelled = _DEVICE_CODE_RE.findall(output)
    # Current Codex CLI wording puts the code away from the word "code".
    # The 4-5 uppercase format is specific to the official device flow.
    return labelled or _HYPHENATED_DEVICE_CODE_RE.findall(output)


async def ensure_auth_volume(subscription_id: str):
    name = auth_volume_name(subscription_id)
    try:
        return await volume_get(name)
    except docker.errors.NotFound:
        volume = await volume_create(
            name=name,
            labels={
                "trinity.platform": "codex-auth",
                "trinity.subscription-id": subscription_id,
            },
        )
        # Docker initializes named volumes as root-owned; Codex runs as 1000
        # and must update its own auth.json when it refreshes the account token.
        await containers_run(
            "alpine:3.20",
            command=["sh", "-c", "chown 1000:1000 /codex && chmod 700 /codex"],
            volumes={name: {"bind": "/codex", "mode": "rw"}},
            user="0:0",
            remove=True,
            network_disabled=True,
        )
        return volume


def _assert_codex_login_subscription(subscription_id: str):
    subscription = db.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Credential not found")
    if subscription.provider != "openai" or subscription.auth_type != "codex_chatgpt_login":
        raise HTTPException(status_code=400, detail="Credential is not a Codex ChatGPT login")
    return subscription


async def start_login(subscription_id: str) -> dict[str, Any]:
    """Start the official device-auth flow in a per-credential state volume."""
    _assert_codex_login_subscription(subscription_id)
    await ensure_auth_volume(subscription_id)
    name = login_container_name(subscription_id)
    try:
        existing = await container_get(name)
    except docker.errors.NotFound:
        existing = None
    if existing is not None:
        await container_reload(existing)
        if existing.status == "running":
            return await login_status(subscription_id)
        await container_remove(existing, force=True)

    container = await container_create(
        CODEX_IMAGE,
        command=["login", "--device-auth"],
        entrypoint="codex",
        name=name,
        environment={"CODEX_HOME": CODEX_HOME},
        volumes={auth_volume_name(subscription_id): {"bind": CODEX_HOME, "mode": "rw"}},
        user="1000:1000",
        labels={
            "trinity.platform": "codex-login",
            "trinity.subscription-id": subscription_id,
        },
        cap_drop=["ALL"],
        security_opt=["no-new-privileges:true"],
    )
    await container_start(container)
    return await login_status(subscription_id)


async def login_status(subscription_id: str) -> dict[str, Any]:
    """Return non-secret CLI-login status; only an official URL escapes logs."""
    _assert_codex_login_subscription(subscription_id)
    try:
        container = await container_get(login_container_name(subscription_id))
    except docker.errors.NotFound:
        return {"status": "not_started", "connected": False}
    await container_reload(container)
    raw = await container_logs(container, tail=40)
    output = _ANSI_ESCAPE_RE.sub("", raw.decode("utf-8", errors="replace"))
    urls = _URL_RE.findall(output)
    device_codes = _extract_device_codes(output)
    state = container.attrs.get("State", {})
    running = state.get("Running", False)
    succeeded = not running and state.get("ExitCode") == 0
    rate_limited = not running and bool(_RATE_LIMIT_RE.search(output))
    if succeeded:
        # Defense in depth around the official CLI's own private-file mode.
        await containers_run(
            "alpine:3.20",
            command=["sh", "-c", "test ! -f /codex/auth.json || chmod 600 /codex/auth.json"],
            volumes={auth_volume_name(subscription_id): {"bind": "/codex", "mode": "rw"}},
            user="0:0",
            remove=True,
            network_disabled=True,
        )
    if running:
        status = "pending"
        message = "Waiting for the device code from the official Codex CLI."
    elif succeeded:
        status = "connected"
        message = "Connected"
    elif rate_limited:
        status = "rate_limited"
        message = "OpenAI temporarily rate-limited device-login attempts. Wait before deleting this credential and starting a new login."
    else:
        status = "failed"
        message = "The official Codex device login ended before authorization completed. Delete this credential and try again later."
    return {
        "status": status,
        "connected": succeeded,
        "login_url": urls[-1] if urls else None,
        "device_code": device_codes[-1] if device_codes else None,
        "message": message,
        "instructions": "Open the official Codex login URL, enter the one-time device code when shown, and complete the account authorization. The resulting credential cache is never returned.",
    }


async def add_auth_mount(subscription_id: Optional[str], runtime: str, volumes: dict, env_vars: dict) -> None:
    """Attach a writable credential-local auth.json only to a Codex agent."""
    if (runtime or "").lower() != "codex" or not subscription_id:
        return
    subscription = db.get_subscription(subscription_id)
    if not subscription or subscription.provider != "openai" or subscription.auth_type != "codex_chatgpt_login":
        return
    assigned = db.get_agents_by_subscription(subscription_id)
    if len(assigned) > 1:
        raise HTTPException(
            status_code=409,
            detail="A ChatGPT/Codex login may be attached to only one agent. Create a separate credential to run agents concurrently.",
        )
    await ensure_auth_volume(subscription_id)
    volumes[auth_volume_name(subscription_id)] = {"bind": CODEX_HOME, "mode": "rw"}
    env_vars["CODEX_HOME"] = CODEX_HOME


async def delete_auth_volume(subscription_id: str) -> None:
    """Remove the disposable login container before deleting its auth volume."""
    try:
        container = await container_get(login_container_name(subscription_id))
    except docker.errors.NotFound:
        container = None
    if container is not None:
        await container_remove(container, force=True)
    try:
        volume = await volume_get(auth_volume_name(subscription_id))
    except docker.errors.NotFound:
        return
    await volume_remove(volume, force=False)
