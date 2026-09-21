from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
from typing import Any
from uuid import uuid4

from smarttutor.services.path_service import get_path_service

from .embedding_endpoint import normalize_embedding_endpoint_for_display

# Fallback only — frozen at admin scope at import time. Production code should
# enter through ``get_model_catalog_service()`` so the path is resolved from the
# current user's PathService on every call.
CATALOG_PATH = get_path_service().get_settings_file("model_catalog")

# A fixed placeholder is returned to settings clients instead of provider
# credentials. It is also accepted on write as "keep the stored value", so a
# load/edit/save round trip never sends a real secret to the browser.
CATALOG_SECRET_MASK = "***"
_SECRET_FIELD_HINTS = ("api_key", "apikey", "token", "secret", "password")
MODEL_DISCOVERY_CACHE_TTL_SECONDS = 300.0
MODEL_DISCOVERY_INITIAL_BACKOFF_SECONDS = 60.0
MODEL_DISCOVERY_MAX_BACKOFF_SECONDS = 900.0


@dataclass(slots=True)
class ModelDiscoveryResult:
    models: list[str]
    from_cache: bool = False
    skipped: bool = False
    error: str | None = None
    retry_after: float | None = None


@dataclass(slots=True)
class _ModelDiscoveryCacheEntry:
    models: list[str] = field(default_factory=list)
    fetched_at: float = 0.0
    failure_count: int = 0
    failed_at: float | None = None
    next_retry_at: float = 0.0
    last_error: str | None = None


_model_discovery_cache: dict[tuple[str, str, str], _ModelDiscoveryCacheEntry] = {}
_model_discovery_cache_lock = threading.RLock()


def _credential_hash(value: str | None) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def model_discovery_cache_key(
    provider_name: str,
    base_url: str,
    credential: str | None,
) -> tuple[str, str, str]:
    return (
        provider_name.strip().lower(),
        base_url.strip().rstrip("/"),
        _credential_hash(credential),
    )


async def discover_models_with_cache(
    provider_name: str,
    base_url: str,
    credential: str | None,
    fetcher: Callable[[str, str, str | None], Any],
    *,
    force_refresh: bool = False,
    ttl_seconds: float = MODEL_DISCOVERY_CACHE_TTL_SECONDS,
    initial_backoff_seconds: float = MODEL_DISCOVERY_INITIAL_BACKOFF_SECONDS,
    max_backoff_seconds: float = MODEL_DISCOVERY_MAX_BACKOFF_SECONDS,
) -> ModelDiscoveryResult:
    """Fetch provider models with process-local TTL caching and failure backoff."""

    key = model_discovery_cache_key(provider_name, base_url, credential)
    now = time.monotonic()
    with _model_discovery_cache_lock:
        entry = _model_discovery_cache.get(key)
        if entry is not None and entry.fetched_at > 0 and not force_refresh:
            if now - entry.fetched_at < ttl_seconds:
                return ModelDiscoveryResult(models=list(entry.models), from_cache=True)
            if entry.next_retry_at > now:
                return ModelDiscoveryResult(
                    models=list(entry.models),
                    from_cache=True,
                    skipped=True,
                    error=entry.last_error,
                    retry_after=entry.next_retry_at - now,
                )
        elif entry is not None and entry.next_retry_at > now and not force_refresh:
            return ModelDiscoveryResult(
                models=[],
                skipped=True,
                error=entry.last_error,
                retry_after=entry.next_retry_at - now,
            )

    try:
        fetched = await fetcher(provider_name, base_url, credential)
    except Exception as exc:
        message = str(exc)
        now = time.monotonic()
        with _model_discovery_cache_lock:
            entry = _model_discovery_cache.setdefault(key, _ModelDiscoveryCacheEntry())
            entry.failure_count += 1
            backoff = min(
                max_backoff_seconds,
                initial_backoff_seconds * (2 ** max(0, entry.failure_count - 1)),
            )
            entry.failed_at = now
            entry.next_retry_at = now + backoff
            entry.last_error = message
            cached_models = list(entry.models)
        return ModelDiscoveryResult(
            models=cached_models,
            from_cache=bool(cached_models),
            skipped=bool(cached_models),
            error=message,
            retry_after=backoff,
        )

    models = [str(model).strip() for model in fetched if str(model).strip()]
    now = time.monotonic()
    with _model_discovery_cache_lock:
        _model_discovery_cache[key] = _ModelDiscoveryCacheEntry(
            models=models,
            fetched_at=now,
        )
    return ModelDiscoveryResult(models=models)


def clear_model_discovery_cache() -> None:
    with _model_discovery_cache_lock:
        _model_discovery_cache.clear()


def _is_secret_field(name: str) -> bool:
    normalized = name.lower()
    return any(hint in normalized for hint in _SECRET_FIELD_HINTS)


def _redact_secret_value(value: Any) -> Any:
    if isinstance(value, str):
        return CATALOG_SECRET_MASK if value else value
    if isinstance(value, dict):
        return {key: _redact_secret_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_secret_value(item) for item in value]
    return value


def _redact_profile(profile: dict[str, Any]) -> None:
    for key, value in list(profile.items()):
        # Header values are credentials often enough that none of them should
        # cross the API boundary. This also covers JSON-string header maps.
        if key == "extra_headers" or _is_secret_field(key):
            profile[key] = _redact_secret_value(value)


def redact_catalog_secrets(catalog: dict[str, Any]) -> dict[str, Any]:
    """Return an API-safe catalog without mutating stored configuration."""

    redacted = deepcopy(catalog)
    for service in redacted.get("services", {}).values():
        if not isinstance(service, dict):
            continue
        for profile in service.get("profiles", []):
            if isinstance(profile, dict):
                _redact_profile(profile)
    return redacted


def _restore_secret_value(proposed: Any, current: Any) -> Any:
    if proposed == CATALOG_SECRET_MASK:
        return deepcopy(current)
    if isinstance(proposed, dict) and isinstance(current, dict):
        return {
            key: _restore_secret_value(value, current.get(key)) for key, value in proposed.items()
        }
    if isinstance(proposed, list) and isinstance(current, list):
        return [
            _restore_secret_value(value, current[index] if index < len(current) else None)
            for index, value in enumerate(proposed)
        ]
    return proposed


def _restore_profile_secrets(proposed: dict[str, Any], current: dict[str, Any]) -> None:
    for key, value in list(proposed.items()):
        if key == "extra_headers" or _is_secret_field(key):
            proposed[key] = _restore_secret_value(value, current.get(key))


def restore_catalog_secrets(
    proposed_catalog: dict[str, Any], current_catalog: dict[str, Any]
) -> dict[str, Any]:
    """Replace secret placeholders with stored values from the same profile."""

    restored = deepcopy(proposed_catalog)
    current_services = current_catalog.get("services", {})
    for service_name, proposed_service in restored.get("services", {}).items():
        if not isinstance(proposed_service, dict):
            continue
        current_service = current_services.get(service_name, {})
        current_profiles = {
            profile.get("id"): profile
            for profile in current_service.get("profiles", [])
            if isinstance(profile, dict) and profile.get("id")
        }
        for profile in proposed_service.get("profiles", []):
            if not isinstance(profile, dict):
                continue
            current_profile = current_profiles.get(profile.get("id"))
            if current_profile is not None:
                _restore_profile_secrets(profile, current_profile)
    return restored


def _service_shell() -> dict[str, Any]:
    return {
        "active_profile_id": None,
        "active_model_id": None,
        "profiles": [],
    }


def _search_shell() -> dict[str, Any]:
    return {
        "active_profile_id": None,
        "profiles": [],
    }


def _default_catalog() -> dict[str, Any]:
    return {
        "version": 1,
        "services": {
            "llm": _service_shell(),
            "embedding": _service_shell(),
            "search": _search_shell(),
            "tts": _service_shell(),
            "stt": _service_shell(),
            "imagegen": _service_shell(),
            "videogen": _service_shell(),
        },
    }


def _ensure_windows_speech_tts_profile(service: dict[str, Any]) -> bool:
    """Expose local Windows SAPI/System.Speech TTS when PowerShell is available."""
    if os.name != "nt" or not shutil.which("powershell"):
        return False
    profiles = service.setdefault("profiles", [])
    if any(profile.get("binding") == "windows_speech" for profile in profiles if isinstance(profile, dict)):
        return False
    profiles.append(
        {
            "id": "tts-profile-windows-speech",
            "name": "Windows SAPI",
            "binding": "windows_speech",
            "base_url": "powershell",
            "api_key": "sk-no-key-required",
            "api_version": "",
            "extra_headers": {},
            "models": [
                {
                    "id": "tts-model-windows-speech-system",
                    "name": "System.Speech",
                    "model": "system-speech",
                    "voice": "",
                    "response_format": "wav",
                    "speed": 0,
                    "volume": 100,
                }
            ],
        }
    )
    return True


class ModelCatalogService:
    _instances: dict[str, "ModelCatalogService"] = {}

    def __init__(self, path: Path | None = None):
        self.path = path or CATALOG_PATH
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls, path: Path | None = None) -> "ModelCatalogService":
        resolved = (path or get_path_service().get_settings_file("model_catalog")).resolve()
        key = str(resolved)
        if key not in cls._instances:
            cls._instances[key] = cls(resolved)
        return cls._instances[key]

    def load(self) -> dict[str, Any]:
        loaded = self._read_existing_catalog()
        if loaded:
            catalog = _default_catalog()
            catalog.update({k: v for k, v in loaded.items() if k != "services"})
            catalog["services"].update(loaded.get("services", {}))
            merged_defaults = catalog != loaded
            before = deepcopy(catalog)
            self._normalize(catalog)
            if merged_defaults or catalog != before:
                self.save(catalog)
            return catalog

        catalog = _default_catalog()
        self._normalize(catalog)
        self.save(catalog)
        return catalog

    def _read_existing_catalog(self) -> dict[str, Any]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return {}
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return loaded if isinstance(loaded, dict) else {}

    def save(self, catalog: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            normalized = deepcopy(catalog)
            self._normalize(normalized)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp_name = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=self.path.parent,
            )
            temp_path = Path(temp_name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                    json.dump(normalized, handle, indent=2, ensure_ascii=False)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temp_path, self.path)
            finally:
                temp_path.unlink(missing_ok=True)
            return normalized

    def update(self, mutator: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
        with self._lock:
            catalog = self.load()
            mutator(catalog)
            return self.save(catalog)

    def apply(self, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
        current = self.save(catalog or self.load())
        return {"catalog_path": str(self.path), "services": list(current.get("services", {}))}

    def _normalize(self, catalog: dict[str, Any]) -> bool:
        services = catalog.setdefault("services", {})
        changed = False
        services.setdefault("llm", _service_shell())
        services.setdefault("embedding", _service_shell())
        services.setdefault("search", _search_shell())
        services.setdefault("tts", _service_shell())
        services.setdefault("stt", _service_shell())
        services.setdefault("imagegen", _service_shell())
        services.setdefault("videogen", _service_shell())
        if _ensure_windows_speech_tts_profile(services["tts"]):
            changed = True
        for service_name in ("llm", "embedding", "search", "tts", "stt", "imagegen", "videogen"):
            service = services[service_name]
            profiles = service.setdefault("profiles", [])
            for profile in profiles:
                profile.setdefault("id", f"{service_name}-profile-{uuid4().hex[:8]}")
                profile.setdefault("name", "Untitled Profile")
                profile.setdefault("api_version", "")
                profile.setdefault("base_url", "")
                profile.setdefault("api_key", "")
                if service_name == "search":
                    profile.setdefault("provider", "brave")
                    profile.setdefault("proxy", "")
                    profile["models"] = []
                else:
                    profile.setdefault("binding", "openai")
                    profile.setdefault("extra_headers", {})
                    if service_name == "embedding":
                        models = profile.setdefault("models", [])
                        active_model_id = service.get("active_model_id")
                        active_model = next(
                            (item for item in models if item.get("id") == active_model_id),
                            models[0] if models else {},
                        )
                        before = str(profile.get("base_url") or "")
                        after = normalize_embedding_endpoint_for_display(
                            profile.get("binding"),
                            before,
                            model=active_model.get("model"),
                        )
                        if after != before:
                            profile["base_url"] = after
                            changed = True
                    else:
                        models = profile.setdefault("models", [])
                    for model in models:
                        model.setdefault("id", f"{service_name}-model-{uuid4().hex[:8]}")
                        model.setdefault("name", model.get("model") or "Untitled Model")
                        model.setdefault("model", "")
                        if service_name == "embedding":
                            # Empty default → test_runner auto-fills from the
                            # actual API response on first connection test.
                            model.setdefault("dimension", "")
                            # CSV of supported dims discovered during the last
                            # successful "Test connection" — drives the UI
                            # dropdown. Empty when the model is not in any
                            # adapter's MODELS_INFO map.
                            model.setdefault("supported_dimensions", "")
                        elif service_name == "tts":
                            model.setdefault("voice", "")
                            model.setdefault("response_format", "mp3")
            profile_ids = {profile.get("id") for profile in profiles}
            if profiles and service.get("active_profile_id") not in profile_ids:
                service["active_profile_id"] = profiles[0]["id"]
                changed = True
            if service_name in {"llm", "embedding", "tts", "stt", "imagegen", "videogen"}:
                active_profile = self.get_active_profile(catalog, service_name)
                models = (active_profile or {}).get("models") or []
                model_ids = {model.get("id") for model in models}
                if models and service.get("active_model_id") not in model_ids:
                    service["active_model_id"] = models[0]["id"]
                    changed = True
        return changed

    def get_active_profile(
        self, catalog: dict[str, Any], service_name: str
    ) -> dict[str, Any] | None:
        service = catalog.get("services", {}).get(service_name, {})
        active_id = service.get("active_profile_id")
        for profile in service.get("profiles", []):
            if profile.get("id") == active_id:
                return profile
        profiles = service.get("profiles", [])
        return profiles[0] if profiles else None

    def get_active_model(self, catalog: dict[str, Any], service_name: str) -> dict[str, Any] | None:
        if service_name == "search":
            return None
        service = catalog.get("services", {}).get(service_name, {})
        active_model_id = service.get("active_model_id")
        profile = self.get_active_profile(catalog, service_name)
        if not profile:
            return None
        for model in profile.get("models", []):
            if model.get("id") == active_model_id:
                return model
        models = profile.get("models", [])
        return models[0] if models else None


def get_model_catalog_service() -> ModelCatalogService:
    try:
        from smarttutor.multi_user.context import get_current_user
        from smarttutor.multi_user.paths import get_admin_path_service

        if not get_current_user().is_admin:
            return ModelCatalogService.get_instance(
                get_admin_path_service().get_settings_file("model_catalog")
            )
    except Exception:
        pass
    return ModelCatalogService.get_instance(get_path_service().get_settings_file("model_catalog"))


__all__ = [
    "CATALOG_PATH",
    "CATALOG_SECRET_MASK",
    "MODEL_DISCOVERY_CACHE_TTL_SECONDS",
    "ModelCatalogService",
    "ModelDiscoveryResult",
    "clear_model_discovery_cache",
    "discover_models_with_cache",
    "get_model_catalog_service",
    "model_discovery_cache_key",
    "redact_catalog_secrets",
    "restore_catalog_secrets",
]
