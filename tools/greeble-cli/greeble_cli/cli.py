# Re-export from main package (src/greeble_cli/cli.py)
# This shim allows the tools package to work standalone
# Uses star import with source __all__ to stay in sync automatically
from greeble_cli.cli import *  # noqa: F401,F403
from greeble_cli.cli import __all__  # noqa: F401

if __name__ == "__main__":
    from greeble_cli.cli import main

    raise SystemExit(main())
