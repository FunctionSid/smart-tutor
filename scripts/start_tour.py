#!/usr/bin/env python
"""SmartTutor settings tour.

This script configures the runtime files under ``data/user/settings`` only.
It does not install Python packages, install Node dependencies, or start the
Web app. For day-to-day use prefer:

    smarttutor init
    smarttutor start
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from smarttutor_cli.init_cmd import run_init  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or update SmartTutor settings under data/user/settings.",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Configure for CLI-only use and skip Web port prompts.",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=None,
        help="Runtime workspace root. Defaults to the current directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    print("SmartTutor settings tour")
    print("Writing configuration to data/user/settings; no dependencies will be installed.")
    run_init(cli_only=args.cli, home=args.home)
    if args.cli:
        print("\nNext: smarttutor chat")
    else:
        print("\nNext: smarttutor start")


if __name__ == "__main__":
    main()
