"""
Developer helper CLI: `uv run dev <subcommand>`

Subcommands:
  - lint       -> ruff check .  (adds --fix locally; check-only in CI)
  - format     -> ruff format .
  - typecheck  -> mypy .
  - fix        -> ruff check --fix .
  - precommit  -> pre-commit run --all-files
  - ci         -> ruff check . + ruff format --check . + mypy . + uv build
  - test       -> pytest -q
  - build      -> uv build
  - check      -> ruff check (--fix locally) + ruff format . + mypy . + pytest -q

Pass-through args after the subcommand are forwarded to the underlying tool.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def is_ci() -> bool:
    """Return True if running in a CI environment."""
    return bool(os.getenv("CI"))


def run(cmd: list[str]) -> int:
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        sys.stderr.write(f"error: command not found: {cmd[0]}\n")
        sys.stderr.flush()
        return 127


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    parser = argparse.ArgumentParser(prog="dev", add_help=True)
    parser.add_argument(
        "subcommand",
        choices=[
            "lint",
            "format",
            "typecheck",
            "fix",
            "precommit",
            "ci",
            "test",
            "build",
            "check",
        ],
        help="task to run",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER, help="args to pass through")

    if not argv:
        parser.print_help()
        return 2

    ns = parser.parse_args(argv[:1])
    passthrough = argv[1:]
    # Allow callers to pass a conventional '--' separator (e.g., 'uv run dev format -- --check')
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    match ns.subcommand:
        case "lint":
            check_cmd = [
                "ruff",
                "check",
                *([] if is_ci() else ["--fix"]),
                ".",
                *passthrough,
            ]
            return run(check_cmd)
        case "format":
            return run(["ruff", "format", ".", *passthrough])
        case "typecheck":
            return run(["mypy", ".", *passthrough])
        case "fix":
            return run(["ruff", "check", "--fix", ".", *passthrough])
        case "precommit":
            return run(["pre-commit", "run", "--all-files", *passthrough])
        case "ci":
            if (rc := run(["ruff", "check", "."])) != 0:
                return rc
            if (rc := run(["ruff", "format", "--check", "."])) != 0:
                return rc
            return run_mypy_then(["uv", "build"])
        case "test":
            return run(["pytest", "-q", *passthrough])
        case "build":
            return run(["uv", "build", *passthrough])
        case "check":
            # Match pre-commit order: ruff check --fix, then ruff format
            check_cmd = ["ruff", "check", *([] if is_ci() else ["--fix"]), "."]
            if (rc := run(check_cmd)) != 0:
                return rc
            if (rc := run(["ruff", "format", "."])) != 0:
                return rc
            return run_mypy_then(["pytest", "-q"])
    parser.error("unknown subcommand")
    return 2


def run_mypy_then(final_cmd: list[str]) -> int:
    """Run mypy first, then the provided final command if type-checking passes."""
    if (rc := run(["mypy", "."])) != 0:
        return rc
    return run(final_cmd)


def lint_main() -> int:
    return main(["lint"])  # applies fixes locally; check-only in CI


def format_main() -> int:
    return main(["format"])  # applies changes by default


def typecheck_main() -> int:
    return main(["typecheck"])  # mypy src


def test_main() -> int:
    return main(["test"])  # pytest -q


def check_main() -> int:
    return main(["check"])  # ruff check --fix ., ruff format ., mypy, pytest


def precommit_main() -> int:
    return main(["precommit"])  # pre-commit run --all-files

if __name__ == "__main__":
    raise SystemExit(main())
