"""Local Hey Jarvis wake-word inference via installed OpenWakeWord."""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile

from smarttutor.services.voice.base import VoiceProviderError

HEY_JARVIS_MODEL = "hey_jarvis"
EXPECTED_SAMPLE_RATE = 16_000
DEFAULT_WAKE_THRESHOLD = 0.5
DEFAULT_WAKE_DEBOUNCE_SECONDS = 1.5


def _global_python() -> str:
    configured = os.environ.get("SMARTTUTOR_GLOBAL_PYTHON", "").strip()
    if configured:
        found = shutil.which(configured) or configured
        if os.path.exists(found):
            return found
    found = shutil.which("python")
    if not found:
        raise VoiceProviderError("Global Python is required for OpenWakeWord inference.")
    return found


def probe_hey_jarvis() -> dict[str, object]:
    """Load the installed model and run one silent 80 ms inference frame."""
    result = score_hey_jarvis(bytes(1280 * 2), threshold=DEFAULT_WAKE_THRESHOLD)
    return {
        "model": HEY_JARVIS_MODEL,
        "sample_rate": EXPECTED_SAMPLE_RATE,
        "loadable": True,
        "score": result["score"],
        "detected": result["detected"],
    }


def score_hey_jarvis(
    pcm16: bytes,
    *,
    threshold: float = DEFAULT_WAKE_THRESHOLD,
    debounce_seconds: float = DEFAULT_WAKE_DEBOUNCE_SECONDS,
) -> dict[str, object]:
    """Score 16 kHz mono PCM16 audio against the installed Hey Jarvis model."""
    if not pcm16:
        raise VoiceProviderError("No PCM audio was provided for wake-word inference.")
    python_exe = _global_python()
    with tempfile.TemporaryDirectory(prefix="smarttutor-wake-") as tmp:
        script_path = os.path.join(tmp, "score_hey_jarvis.py")
        with open(script_path, "w", encoding="utf-8") as handle:
            handle.write(
                r'''
import base64
import json
import sys
import numpy as np
from openwakeword import Model

payload = json.loads(sys.stdin.read())
audio = np.frombuffer(base64.b64decode(payload["pcm16"]), dtype=np.int16)
model = Model(wakeword_models=["hey_jarvis"])
scores = model.predict(
    audio,
    threshold={"hey_jarvis": float(payload["threshold"])},
    patience={"hey_jarvis": 1},
)
score = float(scores.get("hey_jarvis", 0.0))
print(json.dumps({
    "model": "hey_jarvis",
    "score": score,
    "detected": score >= float(payload["threshold"]),
}))
'''.lstrip()
            )
        completed = subprocess.run(
            [python_exe, script_path],
            input=json.dumps(
                {
                    "pcm16": base64.b64encode(pcm16).decode("ascii"),
                    "threshold": threshold,
                    "debounce_seconds": debounce_seconds,
                }
            ),
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise VoiceProviderError(f"Hey Jarvis wake-word inference failed: {detail[:1000]}")
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise VoiceProviderError(
            f"Hey Jarvis wake-word inference returned unreadable output: {completed.stdout[:500]}"
        ) from exc


__all__ = [
    "DEFAULT_WAKE_DEBOUNCE_SECONDS",
    "DEFAULT_WAKE_THRESHOLD",
    "EXPECTED_SAMPLE_RATE",
    "HEY_JARVIS_MODEL",
    "probe_hey_jarvis",
    "score_hey_jarvis",
]
