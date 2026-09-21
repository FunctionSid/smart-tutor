from __future__ import annotations

import pytest

from smarttutor.services.config.model_catalog import (
    CATALOG_SECRET_MASK,
    clear_model_discovery_cache,
    discover_models_with_cache,
    model_discovery_cache_key,
    redact_catalog_secrets,
    restore_catalog_secrets,
)


def _catalog() -> dict:
    return {
        "version": 1,
        "services": {
            "llm": {
                "profiles": [
                    {
                        "id": "profile-a",
                        "name": "A",
                        "api_key": "sk-secret-a",
                        "extra_headers": {
                            "Authorization": "Bearer secret",
                            "X-Tenant": "tenant-secret",
                        },
                    },
                    {
                        "id": "profile-b",
                        "name": "B",
                        "api_key": "sk-secret-b",
                        "extra_headers": '{"Authorization":"Bearer secret"}',
                    },
                ]
            }
        },
    }


def test_redact_catalog_secrets_masks_credentials_without_mutating_source() -> None:
    catalog = _catalog()

    redacted = redact_catalog_secrets(catalog)

    first, second = redacted["services"]["llm"]["profiles"]
    assert first["api_key"] == CATALOG_SECRET_MASK
    assert first["extra_headers"] == {
        "Authorization": CATALOG_SECRET_MASK,
        "X-Tenant": CATALOG_SECRET_MASK,
    }
    assert second["extra_headers"] == CATALOG_SECRET_MASK
    assert catalog["services"]["llm"]["profiles"][0]["api_key"] == "sk-secret-a"


def test_restore_catalog_secrets_matches_profiles_by_id_after_reorder() -> None:
    current = _catalog()
    proposed = redact_catalog_secrets(current)
    proposed["services"]["llm"]["profiles"].reverse()
    proposed["services"]["llm"]["profiles"][0]["name"] = "Renamed B"
    proposed["services"]["llm"]["profiles"][1]["api_key"] = "sk-replaced-a"

    restored = restore_catalog_secrets(proposed, current)

    first, second = restored["services"]["llm"]["profiles"]
    assert first["id"] == "profile-b"
    assert first["api_key"] == "sk-secret-b"
    assert first["extra_headers"] == '{"Authorization":"Bearer secret"}'
    assert first["name"] == "Renamed B"
    assert second["api_key"] == "sk-replaced-a"
    assert second["extra_headers"]["Authorization"] == "Bearer secret"


def test_restore_catalog_secrets_keeps_explicit_clear() -> None:
    current = _catalog()
    proposed = redact_catalog_secrets(current)
    proposed["services"]["llm"]["profiles"][0]["api_key"] = ""

    restored = restore_catalog_secrets(proposed, current)

    assert restored["services"]["llm"]["profiles"][0]["api_key"] == ""


@pytest.mark.asyncio
async def test_model_discovery_cache_uses_ttl_and_failure_backoff() -> None:
    clear_model_discovery_cache()
    calls = 0

    async def fetcher(provider: str, base_url: str, api_key: str | None) -> list[str]:
        nonlocal calls
        calls += 1
        return [f"{provider}:{calls}"]

    first = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434/v1",
        None,
        fetcher,
        ttl_seconds=60,
    )
    second = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434/v1",
        None,
        fetcher,
        ttl_seconds=60,
    )
    expired = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434/v1",
        None,
        fetcher,
        ttl_seconds=0,
    )
    forced = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434/v1",
        None,
        fetcher,
        force_refresh=True,
        ttl_seconds=60,
    )

    assert first.models == ["ollama:1"]
    assert second.models == ["ollama:1"]
    assert second.from_cache is True
    assert expired.models == ["ollama:2"]
    assert forced.models == ["ollama:3"]
    assert calls == 3
    clear_model_discovery_cache()


@pytest.mark.asyncio
async def test_model_discovery_failure_backoff_skips_repeat_offline_fetches() -> None:
    clear_model_discovery_cache()
    calls = 0

    async def fetcher(provider: str, base_url: str, api_key: str | None) -> list[str]:
        nonlocal calls
        calls += 1
        raise TimeoutError("provider offline")

    first = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434/v1",
        None,
        fetcher,
        initial_backoff_seconds=60,
    )
    second = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434/v1",
        None,
        fetcher,
        initial_backoff_seconds=60,
    )

    assert first.models == []
    assert first.error == "provider offline"
    assert first.skipped is False
    assert second.models == []
    assert second.skipped is True
    assert second.error == "provider offline"
    assert calls == 1
    clear_model_discovery_cache()


@pytest.mark.asyncio
async def test_model_discovery_offline_provider_returns_stale_catalog() -> None:
    clear_model_discovery_cache()
    calls = 0

    async def fetcher(provider: str, base_url: str, api_key: str | None) -> list[str]:
        nonlocal calls
        calls += 1
        if calls == 1:
            return ["gpt-oss-20b"]
        raise TimeoutError("provider offline")

    first = await discover_models_with_cache(
        "krutrim",
        "https://cloud.olakrutrim.com/v1",
        "secret",
        fetcher,
        ttl_seconds=0,
    )
    offline = await discover_models_with_cache(
        "krutrim",
        "https://cloud.olakrutrim.com/v1",
        "secret",
        fetcher,
        ttl_seconds=0,
        initial_backoff_seconds=60,
    )
    backoff = await discover_models_with_cache(
        "krutrim",
        "https://cloud.olakrutrim.com/v1",
        "secret",
        fetcher,
        ttl_seconds=0,
        initial_backoff_seconds=60,
    )

    assert first.models == ["gpt-oss-20b"]
    assert offline.models == ["gpt-oss-20b"]
    assert offline.from_cache is True
    assert offline.skipped is True
    assert offline.error == "provider offline"
    assert backoff.models == ["gpt-oss-20b"]
    assert backoff.skipped is True
    assert calls == 2
    clear_model_discovery_cache()


def test_model_discovery_cache_key_uses_secret_safe_fingerprint() -> None:
    key = model_discovery_cache_key(
        "Krutrim",
        "https://cloud.olakrutrim.com/v1/",
        "sk-secret-value",
    )
    other_key = model_discovery_cache_key(
        "krutrim",
        "https://cloud.olakrutrim.com/v1",
        "sk-other-secret",
    )

    assert key[0] == "krutrim"
    assert key[1] == "https://cloud.olakrutrim.com/v1"
    assert "sk-secret-value" not in repr(key)
    assert key != other_key


@pytest.mark.asyncio
async def test_model_discovery_cache_keeps_empty_successes_for_ttl() -> None:
    clear_model_discovery_cache()
    calls = 0

    async def fetcher(provider: str, base_url: str, api_key: str | None) -> list[str]:
        nonlocal calls
        calls += 1
        return []

    first = await discover_models_with_cache(
        "krutrim",
        "https://cloud.olakrutrim.com/v1",
        "secret",
        fetcher,
    )
    second = await discover_models_with_cache(
        "krutrim",
        "https://cloud.olakrutrim.com/v1",
        "secret",
        fetcher,
    )

    assert first.models == []
    assert second.models == []
    assert second.from_cache is True
    assert calls == 1

    clear_model_discovery_cache()
    calls = 0

    async def fetcher(provider: str, base_url: str, api_key: str | None) -> list[str]:
        nonlocal calls
        calls += 1
        assert provider == "ollama"
        assert base_url == "http://localhost:11434"
        assert api_key is None
        if calls == 1:
            return ["llama3.2"]
        raise TimeoutError("offline")

    first = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434",
        None,
        fetcher,
        ttl_seconds=0,
        initial_backoff_seconds=60,
    )
    assert first.models == ["llama3.2"]
    assert first.from_cache is False

    second = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434",
        None,
        fetcher,
        ttl_seconds=0,
        initial_backoff_seconds=60,
    )
    assert second.models == ["llama3.2"]
    assert second.from_cache is True
    assert second.skipped is True
    assert second.error == "offline"

    third = await discover_models_with_cache(
        "ollama",
        "http://localhost:11434",
        None,
        fetcher,
        force_refresh=True,
        ttl_seconds=0,
        initial_backoff_seconds=60,
    )
    assert third.models == ["llama3.2"]
    assert third.from_cache is True
    assert calls == 3

    clear_model_discovery_cache()
