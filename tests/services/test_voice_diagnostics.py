from __future__ import annotations

from pathlib import Path

from smarttutor.services.voice import diagnostics


def test_discover_piper_voices_requires_matching_json(
    tmp_path: Path, monkeypatch
) -> None:
    voice_dir = tmp_path / "piper"
    voice_dir.mkdir()
    valid = voice_dir / "en_US-test.onnx"
    valid.write_bytes(b"model")
    valid.with_suffix(".onnx.json").write_text("{}", encoding="utf-8")
    orphan = voice_dir / "orphan.onnx"
    orphan.write_bytes(b"model")
    monkeypatch.setenv("SMARTTUTOR_PIPER_VOICE_DIRS", str(voice_dir))

    voices = diagnostics.discover_piper_voices()

    assert len(voices) == 1
    assert voices[0]["name"] == "en_US-test"
    assert voices[0]["model"] == str(valid)
    assert voices[0]["config"] == str(valid.with_suffix(".onnx.json"))


def test_collect_voice_capabilities_reports_installed_configured_working_layers(
    monkeypatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_which", lambda name: f"C:/bin/{name}.exe")
    monkeypatch.setattr(diagnostics, "_which_all", lambda name: [f"C:/bin/{name}.exe"])
    monkeypatch.setattr(
        diagnostics,
        "_package_info",
        lambda dist, mod: (True, "C:/Python/python.exe", "1.0", f"C:/Python/{mod}.py"),
    )
    monkeypatch.setattr(diagnostics, "_python_import_works", lambda mod: (mod != "whisper", "ok"))
    monkeypatch.setattr(
        diagnostics,
        "discover_windows_voices",
        lambda: [{"name": "Microsoft Zira Desktop", "culture": "en-US", "gender": "Female"}],
    )
    monkeypatch.setattr(diagnostics, "discover_piper_voices", lambda: [])
    catalog = {
        "version": 1,
        "services": {
            "stt": {
                "active_profile_id": "p",
                "active_model_id": "m",
                "profiles": [
                    {
                        "id": "p",
                        "binding": "faster-whisper",
                        "base_url": "python",
                        "api_key": "",
                        "models": [{"id": "m", "model": "tiny"}],
                    }
                ],
            },
            "tts": {
                "active_profile_id": "p",
                "active_model_id": "m",
                "profiles": [
                    {
                        "id": "p",
                        "binding": "edge-tts",
                        "base_url": "edge-tts",
                        "api_key": "",
                        "models": [{"id": "m", "model": "edge-tts", "voice": "en-US-AriaNeural"}],
                    }
                ],
            },
        },
    }

    payload = diagnostics.collect_voice_capabilities(catalog=catalog)

    faster = next(item for item in payload["stt"] if item["name"] == "faster-whisper")
    piper = next(item for item in payload["tts"] if item["name"] == "Piper")
    edge = next(item for item in payload["tts"] if item["name"] == "Edge TTS")
    pyttsx3 = next(item for item in payload["tts"] if item["name"] == "pyttsx3")
    gtts = next(item for item in payload["tts"] if item["name"] == "gTTS")
    whisper = next(item for item in payload["stt"] if item["name"] == "Whisper CLI")
    assert faster["installed"] is True
    assert faster["configured"] is True
    assert faster["implemented"] is True
    assert faster["working"] is True
    assert whisper["status"] == "installed-not-working"
    assert piper["status"] == "installed-no-voice-models"
    assert edge["working"] is True
    assert pyttsx3["status"] == "installed-not-verified"
    assert pyttsx3["working"] is False
    assert gtts["status"] == "installed-not-verified"
    assert gtts["implemented"] is True
