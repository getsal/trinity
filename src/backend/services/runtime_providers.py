"""Canonical mappings between runtimes, providers, and environment variables."""

# Maps agent runtime name → credential provider name
RUNTIME_PROVIDER: dict[str, str] = {
    "claude-code": "claude",
    "codex": "openai",
    "gemini-cli": "google",
}

# Maps provider + token_type → env var name injected into the agent container
PROVIDER_ENV_VARS: dict[str, dict[str, str]] = {
    "claude": {
        "oauth": "CLAUDE_CODE_OAUTH_TOKEN",
        "api_key": "ANTHROPIC_API_KEY",
    },
    "openai": {
        "oauth": "OPENAI_API_KEY",
        "api_key": "OPENAI_API_KEY",
    },
    "google": {
        "oauth": "GEMINI_API_KEY",
        "api_key": "GOOGLE_API_KEY",
    },
}

# Default token_type per provider (used when not explicitly specified)
PROVIDER_DEFAULT_TOKEN_TYPE: dict[str, str] = {
    "claude": "oauth",
    "openai": "api_key",
    "google": "api_key",
}


def get_env_var_for_runtime(runtime: str, token_type: str | None = None) -> str | None:
    """Return the env var name for a given runtime and token_type."""
    provider = RUNTIME_PROVIDER.get(runtime)
    if not provider:
        return None
    effective_token_type = token_type or PROVIDER_DEFAULT_TOKEN_TYPE.get(provider, "api_key")
    return PROVIDER_ENV_VARS.get(provider, {}).get(effective_token_type)


def get_provider_for_runtime(runtime: str) -> str | None:
    """Return the provider name for a given runtime."""
    return RUNTIME_PROVIDER.get(runtime)
