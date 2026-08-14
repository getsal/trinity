"""Credential-volume behavior for official Codex account login."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from services import codex_auth_service


def test_auth_volume_and_login_container_names_are_credential_scoped():
    subscription_id = "12345678-1234-1234-1234-123456789abc"
    assert codex_auth_service.auth_volume_name(subscription_id).endswith(subscription_id)
    assert codex_auth_service.login_container_name(subscription_id).endswith(subscription_id)


def test_login_output_extracts_only_device_code_and_clean_url():
    output = (
        b"\x1b[32mOpen https://auth.openai.com/codex/device\x1b[0m\n"
        b"Device code: A1B2C3D4E5F6\n"
    )

    clean = codex_auth_service._ANSI_ESCAPE_RE.sub("", output.decode())

    assert codex_auth_service._URL_RE.findall(clean) == ["https://auth.openai.com/codex/device"]
    assert codex_auth_service._DEVICE_CODE_RE.findall(clean) == ["A1B2C3D4E5F6"]


def test_login_output_extracts_official_hyphenated_device_code():
    output = "Use this code: A1B2-C3D4E"

    assert codex_auth_service._DEVICE_CODE_RE.findall(output) == ["A1B2-C3D4E"]


@pytest.mark.asyncio
async def test_account_login_mount_sets_private_codex_home(monkeypatch):
    credential = SimpleNamespace(provider="openai", auth_type="codex_chatgpt_login")
    monkeypatch.setattr(codex_auth_service.db, "get_subscription", lambda _id: credential)
    monkeypatch.setattr(codex_auth_service.db, "get_agents_by_subscription", lambda _id: ["codex-agent"])

    ensured = []
    async def fake_ensure(subscription_id):
        ensured.append(subscription_id)
    monkeypatch.setattr(codex_auth_service, "ensure_auth_volume", fake_ensure)

    volumes, env = {}, {}
    await codex_auth_service.add_auth_mount("credential-id", "codex", volumes, env)

    assert ensured == ["credential-id"]
    assert volumes == {
        codex_auth_service.auth_volume_name("credential-id"): {
            "bind": codex_auth_service.CODEX_HOME,
            "mode": "rw",
        }
    }
    assert env["CODEX_HOME"] == codex_auth_service.CODEX_HOME


@pytest.mark.asyncio
async def test_account_login_mount_rejects_concurrent_agents(monkeypatch):
    credential = SimpleNamespace(provider="openai", auth_type="codex_chatgpt_login")
    monkeypatch.setattr(codex_auth_service.db, "get_subscription", lambda _id: credential)
    monkeypatch.setattr(codex_auth_service.db, "get_agents_by_subscription", lambda _id: ["one", "two"])

    with pytest.raises(HTTPException, match="only one agent"):
        await codex_auth_service.add_auth_mount("credential-id", "codex", {}, {})


@pytest.mark.asyncio
async def test_login_status_reports_rate_limit_without_returning_raw_log(monkeypatch):
    credential = SimpleNamespace(provider="openai", auth_type="codex_chatgpt_login")
    container = SimpleNamespace(
        attrs={"State": {"Running": False, "ExitCode": 1}},
        status="exited",
    )
    monkeypatch.setattr(codex_auth_service.db, "get_subscription", lambda _id: credential)

    async def fake_container_get(_name):
        return container

    async def fake_reload(_container):
        return None

    async def fake_logs(_container, tail):
        assert tail == 40
        return b"Error logging in with device code: device auth failed with status 429 Too Many Requests"

    monkeypatch.setattr(codex_auth_service, "container_get", fake_container_get)
    monkeypatch.setattr(codex_auth_service, "container_reload", fake_reload)
    monkeypatch.setattr(codex_auth_service, "container_logs", fake_logs)

    status = await codex_auth_service.login_status("credential-id")

    assert status["status"] == "rate_limited"
    assert status["connected"] is False
    assert "temporarily rate-limited" in status["message"]
    assert "429" not in status["message"]


@pytest.mark.asyncio
async def test_delete_auth_volume_removes_login_container_first(monkeypatch):
    container = object()
    volume = object()
    removed = []

    async def fake_container_get(name):
        assert name == codex_auth_service.login_container_name("credential-id")
        return container

    async def fake_container_remove(value, force):
        removed.append(("container", value, force))

    async def fake_volume_get(name):
        assert name == codex_auth_service.auth_volume_name("credential-id")
        return volume

    async def fake_volume_remove(value, force):
        removed.append(("volume", value, force))

    monkeypatch.setattr(codex_auth_service, "container_get", fake_container_get)
    monkeypatch.setattr(codex_auth_service, "container_remove", fake_container_remove)
    monkeypatch.setattr(codex_auth_service, "volume_get", fake_volume_get)
    monkeypatch.setattr(codex_auth_service, "volume_remove", fake_volume_remove)

    await codex_auth_service.delete_auth_volume("credential-id")

    assert removed == [("container", container, True), ("volume", volume, False)]
