"""Voice capability diagnostics for local/global speech tooling."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from smarttutor.services.config.model_catalog import redact_catalog_secrets
from smarttutor.services.config.provider_runtime import (
    resolve_stt_runtime_config,
    resolve_tts_runtime_config,
)


@dataclass(slots=True)
class ToolDiagnostic:
    name: str
    installed: bool = False
    configured: bool = False
    implemented: bool = False
    tested: bool = False
    working: bool = False
    executable: str = ""
    python: str = ""
    package_owner: str = ""
    version: str = ""
    status: str = "unavailable"
    detail: str = ""
    voices: list[dict[str, str]] = field(default_factory=list)


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _which_all(name: str) -> list[str]:
    matches = shutil.which(name, mode=os.F_OK | os.X_OK, path=os.environ.get("PATH", ""))
    all_matches: list[str] = []
    if matches:
        all_matches.append(matches)
    try:
        completed = subprocess.run(
            ["where.exe", name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return all_matches
    if completed.returncode != 0:
        return all_matches
    for line in completed.stdout.splitlines():
        item = line.strip()
        if item and item not in all_matches:
            all_matches.append(item)
    return all_matches


def _global_python() -> str:
    venv_root = (Path.cwd() / ".venv").resolve()
    for candidate in _which_all("python"):
        path = Path(candidate)
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if venv_root not in resolved.parents:
            return str(resolved)
    return _which("python")


def _powershell_executable() -> str:
    return _which("pwsh") or _which("powershell")


def _package_info(dist_name: str, import_name: str) -> tuple[bool, str, str, str]:
    script = f"""
import importlib.metadata as md
import importlib.util
import json
import sys
dist_name = {dist_name!r}
import_name = {import_name!r}
spec = importlib.util.find_spec(import_name)
try:
    version = md.version(dist_name)
except md.PackageNotFoundError:
    version = ""
print(json.dumps({{
    "python": sys.executable,
    "installed": bool(spec),
    "origin": spec.origin if spec else "",
    "version": version,
}}))
""".strip()
    python = _global_python()
    if not python:
        return False, "", "", ""
    try:
        completed = subprocess.run(
            [python, "-c", script],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception:
        return False, python, "", ""
    if completed.returncode != 0:
        return False, python, "", completed.stderr.strip()[:500]
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except Exception:
        return False, python, "", completed.stdout.strip()[:500]
    return (
        bool(payload.get("installed")),
        str(payload.get("python") or python),
        str(payload.get("version") or ""),
        str(payload.get("origin") or ""),
    )


def _python_import_works(import_name: str) -> tuple[bool, str]:
    python = _global_python()
    if not python:
        return False, "Global python was not found on PATH."
    try:
        completed = subprocess.run(
            [python, "-c", f"import {import_name}; print('ok')"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:
        return False, str(exc)
    if completed.returncode == 0:
        return True, "Import succeeded."
    return False, (completed.stderr or completed.stdout).strip()[:500]


def discover_windows_voices() -> list[dict[str, str]]:
    powershell = _powershell_executable()
    if not powershell:
        return []
    script = """
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.GetInstalledVoices() | ForEach-Object {
  $v = $_.VoiceInfo
  [PSCustomObject]@{
    name = $v.Name
    culture = $v.Culture.Name
    gender = [string]$v.Gender
  }
} | ConvertTo-Json -Compress
""".strip()
    try:
        completed = subprocess.run(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception:
        return []
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return []
    rows = payload if isinstance(payload, list) else [payload]
    return [
        {
            "name": str(row.get("name") or ""),
            "culture": str(row.get("culture") or ""),
            "gender": str(row.get("gender") or ""),
        }
        for row in rows
        if isinstance(row, dict) and row.get("name")
    ]


def _piper_search_roots() -> list[Path]:
    roots: list[Path] = []
    for env_name in ("SMARTTUTOR_PIPER_VOICE_DIRS", "PIPER_VOICE_DIRS", "PIPER_DATA_DIR"):
        raw = os.environ.get(env_name, "")
        for part in raw.split(os.pathsep):
            if part.strip():
                roots.append(Path(part.strip()).expanduser())
    roots.extend(
        [
            Path("data/user/voices/piper"),
            Path("data/voices/piper"),
            Path.home() / "piper",
            Path.home() / "AppData" / "Local" / "piper",
        ]
    )
    seen: set[Path] = set()
    unique: list[Path] = []
    for root in roots:
        resolved = root.resolve() if root.exists() else root
        if resolved not in seen:
            seen.add(resolved)
            unique.append(root)
    return unique


def discover_piper_voices() -> list[dict[str, str]]:
    voices: list[dict[str, str]] = []
    for root in _piper_search_roots():
        if not root.exists():
            continue
        for model in root.rglob("*.onnx"):
            config = model.with_suffix(model.suffix + ".json")
            if not config.exists():
                continue
            voices.append(
                {
                    "name": model.stem,
                    "model": str(model),
                    "config": str(config),
                }
            )
    return voices


def _active_configured(service: str, catalog: dict[str, Any] | None) -> bool:
    try:
        if service == "stt":
            resolve_stt_runtime_config(catalog=catalog)
        else:
            resolve_tts_runtime_config(catalog=catalog)
    except Exception:
        return False
    return True


def collect_voice_capabilities(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return installed/configured/implemented/tested/working voice capability state."""
    redacted_catalog = redact_catalog_secrets(catalog or {})
    global_python = _global_python()

    fw_installed, fw_python, fw_version, fw_origin = _package_info(
        "faster-whisper", "faster_whisper"
    )
    fw_import_ok, fw_import_detail = _python_import_works("faster_whisper")
    whisper_exe = _which("whisper")
    whisper_installed, whisper_python, whisper_version, whisper_origin = _package_info(
        "openai-whisper", "whisper"
    )
    whisper_import_ok, whisper_detail = _python_import_works("whisper")
    ctranslate_installed, ct_python, ct_version, ct_origin = _package_info(
        "ctranslate2", "ctranslate2"
    )
    edge_installed, edge_python, edge_version, edge_origin = _package_info("edge-tts", "edge_tts")
    edge_exe = _which("edge-tts")
    piper_installed, piper_python, piper_version, piper_origin = _package_info("piper-tts", "piper")
    piper_exe = _which("piper")
    pyttsx3_installed, pyttsx3_python, pyttsx3_version, pyttsx3_origin = _package_info(
        "pyttsx3", "pyttsx3"
    )
    pyttsx3_import_ok, pyttsx3_detail = _python_import_works("pyttsx3")
    gtts_installed, gtts_python, gtts_version, gtts_origin = _package_info("gTTS", "gtts")

    windows_voices = discover_windows_voices()
    piper_voices = discover_piper_voices()
    tts_configured = _active_configured("tts", catalog)
    stt_configured = _active_configured("stt", catalog)

    stt = [
        ToolDiagnostic(
            name="faster-whisper",
            installed=fw_installed,
            configured=stt_configured,
            implemented=True,
            tested=fw_import_ok,
            working=fw_import_ok and bool(global_python),
            executable=global_python,
            python=fw_python,
            package_owner=fw_origin,
            version=fw_version,
            status="working" if fw_import_ok else "installed-not-working",
            detail=fw_import_detail,
        ),
        ToolDiagnostic(
            name="Whisper CLI",
            installed=bool(whisper_exe) or whisper_installed,
            configured=False,
            implemented=False,
            tested=bool(whisper_exe),
            working=whisper_import_ok,
            executable=whisper_exe,
            python=whisper_python,
            package_owner=whisper_origin,
            version=whisper_version,
            status="working" if whisper_import_ok else "installed-not-working",
            detail=whisper_detail,
        ),
        ToolDiagnostic(
            name="ctranslate2",
            installed=ctranslate_installed,
            configured=False,
            implemented=False,
            tested=ctranslate_installed,
            working=ctranslate_installed,
            python=ct_python,
            package_owner=ct_origin,
            version=ct_version,
            status="installed" if ctranslate_installed else "unavailable",
        ),
    ]

    tts = [
        ToolDiagnostic(
            name="Windows System.Speech",
            installed=bool(windows_voices),
            configured=False,
            implemented=True,
            tested=bool(windows_voices),
            working=bool(windows_voices),
            executable=_powershell_executable(),
            status="working" if windows_voices else "unavailable",
            voices=windows_voices,
        ),
        ToolDiagnostic(
            name="Piper",
            installed=bool(piper_exe) or piper_installed,
            configured=False,
            implemented=True,
            tested=bool(piper_exe),
            working=bool(piper_exe) and bool(piper_voices),
            executable=piper_exe,
            python=piper_python,
            package_owner=piper_origin,
            version=piper_version,
            status="working" if piper_voices else "installed-no-voice-models",
            detail=(
                "Found Piper voice model/config pairs."
                if piper_voices
                else "Piper executable/package found, but no .onnx + .onnx.json voice pair was found."
            ),
            voices=piper_voices,
        ),
        ToolDiagnostic(
            name="Edge TTS",
            installed=bool(edge_exe) or edge_installed,
            configured=tts_configured,
            implemented=True,
            tested=bool(edge_exe),
            working=bool(edge_exe),
            executable=edge_exe,
            python=edge_python,
            package_owner=edge_origin,
            version=edge_version,
            status="working" if edge_exe else "unavailable",
            detail="Uses Microsoft Edge online voices and requires internet access.",
        ),
        ToolDiagnostic(
            name="pyttsx3",
            installed=pyttsx3_installed,
            configured=False,
            implemented=True,
            tested=pyttsx3_import_ok,
            working=False,
            executable=global_python,
            python=pyttsx3_python,
            package_owner=pyttsx3_origin,
            version=pyttsx3_version,
            status="installed-not-verified" if pyttsx3_import_ok else "installed-not-working",
            detail=(
                f"{pyttsx3_detail} Import alone does not prove synthesis; run the TTS diagnostic."
                if pyttsx3_import_ok
                else pyttsx3_detail
            ),
            voices=windows_voices,
        ),
        ToolDiagnostic(
            name="gTTS",
            installed=gtts_installed,
            configured=False,
            implemented=True,
            tested=gtts_installed,
            working=False,
            executable=global_python,
            python=gtts_python,
            package_owner=gtts_origin,
            version=gtts_version,
            status="installed-not-verified" if gtts_installed else "unavailable",
            detail="Integrated through global Python; requires internet and a synthesis diagnostic to prove working.",
        ),
        ToolDiagnostic(
            name="OpenAI TTS",
            installed=True,
            configured=tts_configured,
            implemented=True,
            tested=False,
            working=False,
            status="configured" if tts_configured else "unconfigured",
            detail="OpenAI-compatible TTS is implemented; live working status requires a provider test.",
        ),
    ]

    return {
        "global_python": global_python,
        "stt": [asdict(item) for item in stt],
        "tts": [asdict(item) for item in tts],
        "redacted_catalog": redacted_catalog,
    }


__all__ = [
    "collect_voice_capabilities",
    "discover_piper_voices",
    "discover_windows_voices",
]
