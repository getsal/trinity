"""Provider-agnostic credential request validation."""

import pytest
from pydantic import ValidationError

from db_models import CodexChatGPTLoginStart, SubscriptionCredentialCreate


def test_legacy_claude_oauth_request_keeps_its_defaults():
    credential = SubscriptionCredentialCreate(
        name="claude-max",
        token="sk-ant-oat01-test",
    )

    assert credential.provider == "anthropic"
    assert credential.auth_type == "claude_oauth"


@pytest.mark.parametrize(
    ("provider", "auth_type", "token"),
    [
        ("openai", "api_key", "sk-test"),
        ("google", "api_key", "gemini-test"),
    ],
)
def test_non_claude_runtime_credential_requests_are_valid(provider, auth_type, token):
    credential = SubscriptionCredentialCreate(
        name=f"{provider}-credential",
        token=token,
        provider=provider,
        auth_type=auth_type,
    )

    assert credential.provider == provider
    assert credential.auth_type == auth_type


def test_rejects_credential_type_that_cannot_be_injected_by_an_official_cli():
    with pytest.raises(ValidationError, match="Unsupported provider/auth_type combination"):
        SubscriptionCredentialCreate(
            name="unsupported",
            token="value",
            provider="openai",
            auth_type="oauth_cookie",
        )


def test_chatgpt_login_is_not_accepted_as_an_openai_api_key():
    with pytest.raises(ValidationError, match="Unsupported provider/auth_type combination"):
        SubscriptionCredentialCreate(
            name="account-login",
            token="not-an-api-key",
            provider="openai",
            auth_type="codex_chatgpt_login",
        )

    assert CodexChatGPTLoginStart(name="account-login").name == "account-login"
