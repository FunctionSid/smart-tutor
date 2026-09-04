"""Adapters that invoke globally installed local voice tools.

These adapters deliberately do not import optional voice packages into
SmartTutor's virtual environment. They call the configured global executable or
Python interpreter in a subprocess so a user's existing machine-wide Whisper/TTS
installation can be reused without duplicate installs.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from smarttutor.services.voice.base import BaseSTTAdapter, BaseTTSAdapter, VoiceProviderError
from smarttutor.services.voice.config import STTConfig, TTSConfig


def _resolve_executable(configured: str, fallback_name: str) -> str:
    configured = (configured or "").strip()
    if configured:
        expanded = os.path.expandvars(os.path.expanduser(configured))
        if Path(expanded).exists():
            return expanded
        found = shutil.which(expanded)
        if found:
            return found
        raise VoiceProviderError(
            f"Configured global voice executable was not found: {configured}. "
            "Update Settings > Voice or switch to an OpenAI-compatible voice provider."
        )
    found = shutil.which(fallback_name)
    if not found:
        raise VoiceProviderError(
            f"Global voice executable `{fallback_name}` was not found on PATH. "
            "Install/configure it globally or switch to an OpenAI-compatible voice provider."
        )
    return found


def _suffix_from_filename(filename: str) -> str:
    suffix = Path(filename or "").suffix.lower()
    return suffix if suffix and len(suffix) <= 10 else ".wav"


async def _run_subprocess(args: list[str], *, input_text: str | None = None, timeout: int) -> str:
    def run() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )

    try:
        completed = await asyncio.to_thread(run)
    except subprocess.TimeoutExpired as exc:
        raise VoiceProviderError(f"Global voice tool timed out after {timeout}s.") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise VoiceProviderError(
            f"Global voice tool failed with exit code {completed.returncode}: {detail[:1000]}"
        )
    return completed.stdout


class GlobalFasterWhisperSTTAdapter(BaseSTTAdapter):
    """Transcribe via globally installed ``faster-whisper``.

    ``config.base_url`` may point to the global Python executable. If blank, the
    adapter resolves ``python`` from PATH. ``config.model`` is the Whisper model
    name or local model path, for example ``base`` or ``small``.
    """

    async def transcribe(
        self,
        audio: bytes,
        config: STTConfig,
        *,
        filename: str = "audio.webm",
        content_type: str = "application/octet-stream",
    ) -> str:
        if not audio:
            raise VoiceProviderError("No audio data to transcribe.")
        python_exe = _resolve_executable(config.base_url, "python")
        model_name = (config.model or "base").strip()
        with tempfile.TemporaryDirectory(prefix="smarttutor-stt-") as tmp:
            tmp_dir = Path(tmp)
            audio_path = tmp_dir / f"input{_suffix_from_filename(filename)}"
            script_path = tmp_dir / "transcribe_faster_whisper.py"
            audio_path.write_bytes(audio)
            script_path.write_text(
                """
import json
import sys
from faster_whisper import WhisperModel

audio_path, model_name, language = sys.argv[1:4]
kwargs = {"device": "cpu", "compute_type": "int8"}
model = WhisperModel(model_name, **kwargs)
segments, info = model.transcribe(
    audio_path,
    language=(language or None),
    vad_filter=True,
)
text = " ".join(segment.text.strip() for segment in segments if segment.text).strip()
print(json.dumps({"text": text, "language": getattr(info, "language", None)}))
""".lstrip(),
                encoding="utf-8",
            )
            stdout = await _run_subprocess(
                [python_exe, str(script_path), str(audio_path), model_name, config.language or ""],
                timeout=config.request_timeout,
            )
        try:
            payload = json.loads(stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError) as exc:
            raise VoiceProviderError(
                f"Global faster-whisper returned an unreadable response: {stdout[:500]}"
            ) from exc
        return str(payload.get("text") or "").strip()


class GlobalEdgeTTSTTSAdapter(BaseTTSAdapter):
    """Synthesize via globally installed ``edge-tts`` CLI."""

    async def synthesize(self, text: str, config: TTSConfig) -> tuple[bytes, str]:
        edge_exe = _resolve_executable(config.base_url, "edge-tts")
        voice = (config.voice or config.model or "en-US-AriaNeural").strip()
        with tempfile.TemporaryDirectory(prefix="smarttutor-edge-tts-") as tmp:
            output_path = Path(tmp) / "speech.mp3"
            await _run_subprocess(
                [
                    edge_exe,
                    "--voice",
                    voice,
                    "--text",
                    text,
                    "--write-media",
                    str(output_path),
                ],
                timeout=config.request_timeout,
            )
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise VoiceProviderError("Global edge-tts did not produce audio.")
            return output_path.read_bytes(), "audio/mpeg"


class GlobalPiperTTSAdapter(BaseTTSAdapter):
    """Synthesize via globally installed ``piper`` CLI.

    ``config.model`` must be a Piper ONNX voice model path. ``config.voice`` may
    also hold the model path for compatibility with Settings fields.
    """

    async def synthesize(self, text: str, config: TTSConfig) -> tuple[bytes, str]:
        piper_exe = _resolve_executable(config.base_url, "piper")
        model_path = (config.model or config.voice or "").strip()
        if not model_path:
            raise VoiceProviderError(
                "Piper is installed, but no voice model path is configured. "
                "Set the TTS model to a Piper .onnx file path or switch to Edge TTS."
            )
        expanded_model = os.path.expandvars(os.path.expanduser(model_path))
        if not Path(expanded_model).exists():
            raise VoiceProviderError(f"Configured Piper voice model was not found: {model_path}")
        with tempfile.TemporaryDirectory(prefix="smarttutor-piper-") as tmp:
            output_path = Path(tmp) / "speech.wav"
            await _run_subprocess(
                [piper_exe, "--model", expanded_model, "--output-file", str(output_path)],
                input_text=text,
                timeout=config.request_timeout,
            )
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise VoiceProviderError("Global piper did not produce audio.")
            return output_path.read_bytes(), "audio/wav"


class GlobalPyttsx3TTSAdapter(BaseTTSAdapter):
    """Synthesize via globally installed ``pyttsx3`` using the global Python."""

    async def synthesize(self, text: str, config: TTSConfig) -> tuple[bytes, str]:
        python_exe = _resolve_executable(config.base_url, "python")
        voice = (config.voice or "").strip()
        with tempfile.TemporaryDirectory(prefix="smarttutor-pyttsx3-") as tmp:
            tmp_dir = Path(tmp)
            input_path = tmp_dir / "input.txt"
            output_path = tmp_dir / "speech.wav"
            script_path = tmp_dir / "speak_pyttsx3.py"
            input_path.write_text(text, encoding="utf-8")
            script_path.write_text(
                """
import sys
import pyttsx3

input_path, output_path, voice_name = sys.argv[1:4]
text = open(input_path, "r", encoding="utf-8").read()
engine = pyttsx3.init("sapi5")
if voice_name:
    lowered = voice_name.lower()
    for voice in engine.getProperty("voices"):
        haystack = f"{getattr(voice, 'id', '')} {getattr(voice, 'name', '')}".lower()
        if lowered in haystack:
            engine.setProperty("voice", voice.id)
            break
engine.save_to_file(text, output_path)
engine.runAndWait()
engine.stop()
""".lstrip(),
                encoding="utf-8",
            )
            await _run_subprocess(
                [python_exe, str(script_path), str(input_path), str(output_path), voice],
                timeout=config.request_timeout,
            )
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise VoiceProviderError("Global pyttsx3 did not produce audio.")
            return output_path.read_bytes(), "audio/wav"


class GlobalGTTSTTSAdapter(BaseTTSAdapter):
    """Synthesize via globally installed ``gTTS`` using the global Python."""

    async def synthesize(self, text: str, config: TTSConfig) -> tuple[bytes, str]:
        python_exe = _resolve_executable(config.base_url, "python")
        language = (config.voice or config.model or "en").strip()
        with tempfile.TemporaryDirectory(prefix="smarttutor-gtts-") as tmp:
            tmp_dir = Path(tmp)
            input_path = tmp_dir / "input.txt"
            output_path = tmp_dir / "speech.mp3"
            script_path = tmp_dir / "speak_gtts.py"
            input_path.write_text(text, encoding="utf-8")
            script_path.write_text(
                """
import sys
from gtts import gTTS

input_path, output_path, language = sys.argv[1:4]
text = open(input_path, "r", encoding="utf-8").read()
gTTS(text=text, lang=language or "en").save(output_path)
""".lstrip(),
                encoding="utf-8",
            )
            await _run_subprocess(
                [python_exe, str(script_path), str(input_path), str(output_path), language],
                timeout=config.request_timeout,
            )
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise VoiceProviderError("Global gTTS did not produce audio.")
            return output_path.read_bytes(), "audio/mpeg"


class WindowsSystemSpeechTTSAdapter(BaseTTSAdapter):
    """Synthesize through Windows ``System.Speech`` voices."""

    async def synthesize(self, text: str, config: TTSConfig) -> tuple[bytes, str]:
        powershell = _resolve_executable(config.base_url, "powershell")
        voice = (config.voice or "").strip()
        rate = max(-10, min(10, round(config.speed))) if config.speed is not None else None
        volume = max(0, min(100, int(config.volume))) if config.volume is not None else None
        with tempfile.TemporaryDirectory(prefix="smarttutor-system-speech-") as tmp:
            tmp_dir = Path(tmp)
            input_path = tmp_dir / "input.txt"
            output_path = tmp_dir / "speech.wav"
            input_path.write_text(text, encoding="utf-8")
            input_arg = str(input_path).replace("'", "''")
            output_arg = str(output_path).replace("'", "''")
            script = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$text = Get-Content -Raw -Encoding UTF8 '{input_arg}'; "
            )
            if voice:
                voice_arg = voice.replace("'", "''")
                script += f"$s.SelectVoice('{voice_arg}'); "
            if rate is not None:
                script += f"$s.Rate = {rate}; "
            if volume is not None:
                script += f"$s.Volume = {volume}; "
            script += f"$s.SetOutputToWaveFile('{output_arg}'); $s.Speak($text); $s.Dispose();"
            await _run_subprocess(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                timeout=config.request_timeout,
            )
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise VoiceProviderError("Windows System.Speech did not produce audio.")
            return output_path.read_bytes(), "audio/wav"


__all__ = [
    "GlobalFasterWhisperSTTAdapter",
    "GlobalEdgeTTSTTSAdapter",
    "GlobalPiperTTSAdapter",
    "GlobalPyttsx3TTSAdapter",
    "GlobalGTTSTTSAdapter",
    "WindowsSystemSpeechTTSAdapter",
]
