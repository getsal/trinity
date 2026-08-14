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


def auth_volume_name(subscription_id: str) -> str:
    return f"{_AUTH_VOLUME_PREFIX}{subscription_id}"


def login_container_name(subscription_id: str) -> str:
    return f"{_LOGIN_CONTAINER_PREFIX}{subscription_id}"


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
    urls = _URL_RE.findall(raw.decode("utf-8", errors="replace"))
    state = container.attrs.get("State", {})
    running = state.get("Running", False)
    succeeded = not running and state.get("ExitCode") == 0
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
    return {
        "status": "pending" if running else ("connected" if succeeded else "failed"),
        "connected": succeeded,
        "login_url": urls[-1] if urls else None,
        "instructions": "Open the official Codex login URL and complete the account authorization, then refresh this status.",
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
    try:
        volume = await volume_get(auth_volume_name(subscription_id))
    except docker.errors.NotFound:
        return
    await volume_remove(volume, force=False)
