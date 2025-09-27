from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app = FastAPI(title="Greeble Starter", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


DEFAULT_DOCS_URL = "https://docs.greeble.dev"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    docs_url = os.getenv("GREEBLE_DOCS_URL", DEFAULT_DOCS_URL)
    github_url = os.getenv("GITHUB_REPO_URL", "https://github.com/bakobiibizo/greeble")
    demo_url = os.getenv(
        "GREEBLE_DEMO_URL", "https://github.com/bakobiibizo/greeble/tree/release-candidate/examples"
    )
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "docs_url": docs_url,
            "github_url": github_url,
            "demo_url": demo_url,
        },
    )


@app.get("/docs", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    target = os.getenv("GREEBLE_DOCS_URL", DEFAULT_DOCS_URL)
    return RedirectResponse(target, status_code=307)
