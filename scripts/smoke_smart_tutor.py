"""Small local smoke checks for a running Smart Tutor instance."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class Check:
    name: str
    url: str
    ok_statuses: tuple[int, ...] = (200,)
    skip_statuses: tuple[int, ...] = ()
    json_keys: tuple[str, ...] = ()


def _fetch(url: str, timeout: float) -> tuple[int, Any]:
    request = Request(url, headers={"Accept": "application/json,text/html"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            status = response.status
            content_type = response.headers.get("content-type", "")
    except HTTPError as exc:
        body = exc.read()
        status = exc.code
        content_type = exc.headers.get("content-type", "")
    except TimeoutError as exc:
        return 0, str(exc) or "timed out"
    except URLError as exc:
        return 0, str(exc.reason)

    if "json" in content_type:
        try:
            return status, json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return status, body.decode("utf-8", errors="replace")
    return status, body.decode("utf-8", errors="replace")


def _has_keys(payload: Any, keys: tuple[str, ...]) -> bool:
    return isinstance(payload, dict) and all(key in payload for key in keys)


def run_checks(checks: list[Check], timeout: float) -> tuple[int, int, int]:
    passed = 0
    skipped = 0
    failed = 0
    for check in checks:
        status, payload = _fetch(check.url, timeout)
        if status in check.skip_statuses:
            print(f"SKIP {check.name}: HTTP {status}")
            skipped += 1
            continue
        if status not in check.ok_statuses:
            print(f"FAIL {check.name}: HTTP {status} {payload}")
            failed += 1
            continue
        if check.json_keys and not _has_keys(payload, check.json_keys):
            print(f"FAIL {check.name}: missing keys {', '.join(check.json_keys)}")
            failed += 1
            continue
        print(f"PASS {check.name}: HTTP {status}")
        passed += 1
    return passed, skipped, failed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend", default="http://localhost:3782")
    parser.add_argument("--backend", default="http://127.0.0.1:8001")
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args(argv)

    frontend = args.frontend.rstrip("/")
    backend = args.backend.rstrip("/")
    checks = [
        Check("frontend home", f"{frontend}/"),
        Check("frontend app route", f"{frontend}/home"),
        Check("backend root", f"{backend}/", json_keys=("message",)),
        Check("system status", f"{backend}/api/v1/system/status", json_keys=("backend",)),
        Check("runtime diagnostics", f"{backend}/api/v1/system/diagnostics", json_keys=("available",)),
        Check("knowledge list", f"{backend}/api/v1/knowledge/list"),
        Check("exam list", f"{backend}/api/v1/exam/list"),
        Check("llm options", f"{backend}/api/v1/settings/llm-options", json_keys=("options",)),
        Check(
            "hands-free wake probe",
            f"{backend}/api/v1/voice/wake/hey-jarvis/probe",
            skip_statuses=(404, 502),
        ),
    ]
    passed, skipped, failed = run_checks(checks, args.timeout)
    print(f"\n{passed} passed, {skipped} skipped, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
