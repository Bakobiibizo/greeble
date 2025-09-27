from __future__ import annotations

import argparse

import uvicorn


def main(argv: list[str] | None = None) -> None:
    """Console entry point for the Greeble Starter app.

    Defaults: host 127.0.0.1, port 8050, reload on.
    """
    parser = argparse.ArgumentParser(
        prog="greeble-starter", description="Run the Greeble Starter app"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8050, help="Port (default: 8050)")
    parser.add_argument(
        "--reload",
        dest="reload",
        action="store_true",
        default=True,
        help="Enable auto-reload (default)",
    )
    parser.add_argument(
        "--no-reload",
        dest="reload",
        action="store_false",
        help="Disable auto-reload",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Uvicorn log level (default: info)",
    )
    args = parser.parse_args(argv)

    uvicorn.run(
        "greeble_starter.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )
