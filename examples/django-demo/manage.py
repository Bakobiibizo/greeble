#!/usr/bin/env python3
from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Django is not installed. Run with 'uv run -G django' or 'uv sync -G django'."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
