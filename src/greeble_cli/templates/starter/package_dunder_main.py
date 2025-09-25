from __future__ import annotations

import uvicorn


def main() -> None:
    """Console entry point for the Greeble Starter app.

    Runs the FastAPI app with uvicorn in reload mode by default.
    """
    uvicorn.run("greeble_starter.app:app", reload=True)
