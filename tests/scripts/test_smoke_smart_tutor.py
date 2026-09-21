from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "smoke_smart_tutor.py"
_SPEC = importlib.util.spec_from_file_location("smoke_smart_tutor", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
smoke_smart_tutor = importlib.util.module_from_spec(_SPEC)
sys.modules["smoke_smart_tutor"] = smoke_smart_tutor
_SPEC.loader.exec_module(smoke_smart_tutor)


def test_run_checks_reports_pass_skip_and_fail(
    capsys,
    monkeypatch,
) -> None:
    responses = {
        "http://test/pass": (200, {"ok": True}),
        "http://test/skip": (502, {"detail": "optional provider unavailable"}),
        "http://test/fail": (500, {"detail": "broken"}),
    }
    monkeypatch.setattr(
        smoke_smart_tutor,
        "_fetch",
        lambda url, timeout: responses[url],
    )

    passed, skipped, failed = smoke_smart_tutor.run_checks(
        [
            smoke_smart_tutor.Check("passes", "http://test/pass", json_keys=("ok",)),
            smoke_smart_tutor.Check("skips", "http://test/skip", skip_statuses=(502,)),
            smoke_smart_tutor.Check("fails", "http://test/fail"),
        ],
        timeout=1,
    )

    output = capsys.readouterr().out
    assert passed == 1
    assert skipped == 1
    assert failed == 1
    assert "PASS passes: HTTP 200" in output
    assert "SKIP skips: HTTP 502" in output
    assert "FAIL fails: HTTP 500" in output


def test_run_checks_fails_when_expected_json_key_is_missing(
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        smoke_smart_tutor,
        "_fetch",
        lambda url, timeout: (200, {"other": True}),
    )

    passed, skipped, failed = smoke_smart_tutor.run_checks(
        [smoke_smart_tutor.Check("diagnostics", "http://test/diag", json_keys=("available",))],
        timeout=1,
    )

    assert passed == 0
    assert skipped == 0
    assert failed == 1
    assert "missing keys available" in capsys.readouterr().out


def test_fetch_reports_socket_timeout(monkeypatch) -> None:
    def _timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(smoke_smart_tutor, "urlopen", _timeout)

    status, payload = smoke_smart_tutor._fetch("http://test/slow", timeout=1)

    assert status == 0
    assert payload == "timed out"
