# Re-export from main package (src/greeble_cli/cli.py)
# This shim allows the tools package to work standalone
from greeble_cli.cli import main  # noqa: F401

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
