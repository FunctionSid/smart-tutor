"""Windows SAPI/System.Speech voice discovery."""

from __future__ import annotations

import json
import shutil
import subprocess

from smarttutor.services.voice.base import VoiceProviderError


def discover_sapi_voices() -> list[dict[str, str]]:
    """Return installed Windows System.Speech voices without hard-coded names."""
    powershell = shutil.which("powershell")
    if not powershell:
        raise VoiceProviderError("PowerShell is required to discover Windows SAPI voices.")
    script = r"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voices = @()
foreach ($voice in $s.GetInstalledVoices()) {
  $i = $voice.VoiceInfo
  $voices += [PSCustomObject]@{
    id = $i.Name
    name = $i.Name
    culture = [string]$i.Culture
    gender = [string]$i.Gender
    age = [string]$i.Age
  }
}
$s.Dispose()
$voices | ConvertTo-Json -Compress
"""
    completed = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise VoiceProviderError(f"Windows SAPI voice discovery failed: {detail[:1000]}")
    raw = completed.stdout.strip()
    if not raw:
        return []
    payload = json.loads(raw)
    if isinstance(payload, dict):
        payload = [payload]
    voices: list[dict[str, str]] = []
    for item in payload if isinstance(payload, list) else []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("id") or "").strip()
        if not name:
            continue
        voices.append(
            {
                "id": str(item.get("id") or name),
                "name": name,
                "culture": str(item.get("culture") or ""),
                "gender": str(item.get("gender") or ""),
                "age": str(item.get("age") or ""),
            }
        )
    return voices


__all__ = ["discover_sapi_voices"]
