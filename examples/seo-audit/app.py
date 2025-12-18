#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fastapi>=0.109.0",
#     "uvicorn>=0.27.0",
#     "jinja2>=3.1.0",
#     "python-multipart>=0.0.6",
#     "httpx>=0.27.0",
#     "markdown>=3.5.0",
# ]
# ///
"""
Local SEO Audit Dashboard - Greeble Demo

A demo FastAPI application showcasing the Greeble SEO audit components.
Run with: uv run examples/seo-audit/app.py

This version connects to the hooknladder backend for real audit data.
Set BACKEND_URL environment variable to point to the backend (default: http://localhost:8001)
"""

from __future__ import annotations

import json
import os
import random
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Paths
APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"
DATA_DIR = APP_DIR / "data"
TARGETS_FILE = DATA_DIR / "targets.json"
AUDITS_DIR = DATA_DIR / "audits"

# Backend URL (hooknladder backend)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8050")

# Port configuration
APP_PORT = int(os.getenv("PORT", "8040"))

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
AUDITS_DIR.mkdir(exist_ok=True)

# App setup
app = FastAPI(title="Local SEO Audit Dashboard")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Markdown filter for rendering AI insights
try:
    import markdown

    def md_filter(text: str) -> str:
        """Convert markdown to HTML."""
        if not text:
            return ""
        return markdown.markdown(str(text), extensions=["nl2br"])

    templates.env.filters["markdown"] = md_filter
except ImportError:
    pass


# =============================================================================
# Targets Storage
# =============================================================================


def load_targets() -> list[dict]:
    """Load targets from JSON file."""
    if TARGETS_FILE.exists():
        return json.loads(TARGETS_FILE.read_text())
    return []


def save_targets(targets: list[dict]) -> None:
    """Save targets to JSON file."""
    TARGETS_FILE.write_text(json.dumps(targets, indent=2))


def get_target_by_id(target_id: str) -> dict | None:
    """Get a target by ID."""
    for target in load_targets():
        if target["id"] == target_id:
            return target
    return None


def load_audit(target_id: str) -> dict | None:
    """Load a saved audit for a target."""
    audit_file = AUDITS_DIR / f"{target_id}.json"
    if audit_file.exists():
        return json.loads(audit_file.read_text())
    return None


def save_audit(target_id: str, audit: dict) -> None:
    """Save an audit for a target."""
    audit_file = AUDITS_DIR / f"{target_id}.json"
    audit_file.write_text(json.dumps(audit, indent=2))


async def call_backend_audit(brand: str, website: str = "") -> dict[str, Any] | None:
    """Call the hooknladder backend to run a real audit."""
    payload = {
        "brand": brand,
        "city": brand,  # Use brand as city for search
        "website": website,  # Pass the website URL for scraping
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{BACKEND_URL}/api/audit", json=payload)
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Backend call failed: {e}")
    return None


def generate_mock_audit(query: str) -> dict[str, Any]:
    """Generate mock audit data for demonstration."""
    # Parse query for brand/location
    if " in " in query.lower():
        parts = query.split(" in ", 1)
        brand = parts[0].strip()
        location = parts[1].strip()
    else:
        brand = query.strip()
        location = "San Francisco, CA"

    # Generate score
    base_score = random.randint(55, 92)
    grade_map = {90: "A", 80: "B+", 70: "B", 60: "C+", 50: "C", 0: "D"}
    grade = next(
        g for threshold, g in sorted(grade_map.items(), reverse=True) if base_score >= threshold
    )

    # Generate factors
    factors = [
        {
            "key": "nap_consistency",
            "label": "NAP Consistency",
            "weight": 0.40,
            "value": random.uniform(0.6, 0.95),
        },
        {
            "key": "listing_completeness",
            "label": "Listing Completeness",
            "weight": 0.25,
            "value": random.uniform(0.5, 0.9),
        },
        {
            "key": "citation_coverage",
            "label": "Citation Coverage",
            "weight": 0.25,
            "value": random.uniform(0.4, 0.85),
        },
        {
            "key": "visibility_hint",
            "label": "Visibility Hint",
            "weight": 0.10,
            "value": random.choice([0.5, 1.0]),
        },
    ]

    # Generate recommendations
    recommendations = []
    if factors[0]["value"] < 0.8:
        recommendations.append("Fix NAP inconsistencies on top directories.")
    if factors[2]["value"] < 0.75:
        recommendations.append("Build citations on missing high-value directories.")
    if not recommendations:
        recommendations.append("Maintain current citation quality.")

    # Generate forecast
    forecast = []
    base_traffic = random.randint(80, 150)
    for i in range(1, 13):
        growth = i * random.uniform(6, 12)
        forecast.append(
            {
                "month": f"M{i}",
                "min": int(base_traffic + growth * 0.85),
                "expected": int(base_traffic + growth),
                "max": int(base_traffic + growth * 1.15),
            }
        )

    # Generate diagnostics
    checked = random.randint(8, 20)
    matched = int(checked * random.uniform(0.5, 0.9))
    diagnostics = {
        "checked_count": checked,
        "matched_count": matched,
        "distinct_hosts": random.randint(3, 8),
        "jsonld_count": random.randint(1, 5),
        "nap_consistency": matched / checked if checked else 0,
        "citation_coverage": random.uniform(0.4, 0.85),
    }

    # Generate mock citations
    directories = [
        ("yelp.com", "Yelp"),
        ("tripadvisor.com", "TripAdvisor"),
        ("yellowpages.com", "Yellow Pages"),
        ("foursquare.com", "Foursquare"),
        ("bbb.org", "BBB"),
    ]
    citations = []
    for host, name in random.sample(
        directories, min(len(directories), diagnostics["distinct_hosts"])
    ):
        citations.append(
            {
                "name": brand,
                "url": f"https://{host}/biz/{brand.lower().replace(' ', '-')}",
                "telephone": f"+1 555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "address": {"raw": f"{random.randint(100, 999)} Main St, {location}"},
                "_host": host,
                "_jsonld": random.choice([True, False]),
                "_title": f"{brand} - {name}",
            }
        )

    # Generate insight
    insight = (
        f"Found {checked} citation(s) across {diagnostics['distinct_hosts']} domain(s); "
        f"{matched} matched NAP details. "
        f"JSON-LD present on {diagnostics['jsonld_count']} page(s). "
        f"Overall health is {'strong' if base_score >= 75 else 'moderate' if base_score >= 60 else 'needs improvement'}."
    )

    return {
        "location": {
            "brand": brand,
            "location": location,
            "domain": f"www.{brand.lower().replace(' ', '')}.com",
        },
        "score": {
            "value": base_score,
            "grade": grade,
            "factors": factors,
            "recommendations": recommendations,
        },
        "forecast": forecast,
        "diagnostics": diagnostics,
        "citations": citations,
        "insight": insight,
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


# =============================================================================
# Targets API
# =============================================================================


@app.get("/api/targets", response_class=HTMLResponse)
async def list_targets(request: Request):
    """List all targets."""
    targets = load_targets()
    # Check which targets have audits
    for target in targets:
        target["has_audit"] = load_audit(target["id"]) is not None
    return templates.TemplateResponse(
        "partials/targets-grid.html",
        {"request": request, "targets": targets},
    )


@app.post("/api/targets", response_class=HTMLResponse)
async def add_target(request: Request, name: str = Form(...), url: str = Form(...)):
    """Add a new target."""
    targets = load_targets()
    new_target = {
        "id": str(uuid.uuid4())[:8],
        "name": name.strip(),
        "url": url.strip(),
    }
    targets.append(new_target)
    save_targets(targets)

    # Return updated grid
    for target in targets:
        target["has_audit"] = load_audit(target["id"]) is not None
    return templates.TemplateResponse(
        "partials/targets-grid.html",
        {"request": request, "targets": targets},
    )


@app.delete("/api/targets/{target_id}", response_class=HTMLResponse)
async def delete_target(request: Request, target_id: str):
    """Delete a target."""
    targets = load_targets()
    targets = [t for t in targets if t["id"] != target_id]
    save_targets(targets)

    # Also delete the audit if it exists
    audit_file = AUDITS_DIR / f"{target_id}.json"
    if audit_file.exists():
        audit_file.unlink()

    # Return updated grid
    for target in targets:
        target["has_audit"] = load_audit(target["id"]) is not None
    return templates.TemplateResponse(
        "partials/targets-grid.html",
        {"request": request, "targets": targets},
    )


# =============================================================================
# Audit API
# =============================================================================


@app.get("/api/audit/{target_id}", response_class=HTMLResponse)
async def get_audit(request: Request, target_id: str):
    """Get a saved audit for a target."""
    audit = load_audit(target_id)
    if audit is None:
        return templates.TemplateResponse(
            "partials/empty.html",
            {"request": request, "message": "No audit found. Click 'Run Audit' to generate one."},
        )
    return templates.TemplateResponse(
        "partials/audit-results.html",
        {"request": request, "audit": audit},
    )


@app.post("/api/audit/{target_id}/run", response_class=HTMLResponse)
async def run_target_audit(request: Request, target_id: str):
    """Run an audit for a specific target."""
    target = get_target_by_id(target_id)
    if target is None:
        return templates.TemplateResponse(
            "partials/empty.html",
            {"request": request, "message": "Target not found."},
        )

    # Try real backend first, fall back to mock data
    audit = await call_backend_audit(target["name"], target.get("url", ""))
    if audit is None:
        print(f"Backend unavailable, using mock data for: {target['name']}")
        audit = generate_mock_audit(target["name"])

    # Override location info with target data
    audit["location"] = {
        "brand": target["name"],
        "location": "",
        "domain": target["url"].replace("https://", "").replace("http://", "").split("/")[0],
    }

    # Save the audit
    save_audit(target_id, audit)

    return templates.TemplateResponse(
        "partials/audit-results.html",
        {"request": request, "audit": audit},
    )


@app.post("/api/audit", response_class=HTMLResponse)
async def run_audit(request: Request, q: str = Form(...)):
    """Run an audit by query (legacy endpoint)."""
    if not q.strip():
        return templates.TemplateResponse(
            "partials/empty.html",
            {"request": request, "message": "Please enter a brand or location."},
        )

    # Try real backend first, fall back to mock data
    audit = await call_backend_audit(q, "")
    if audit is None:
        print(f"Backend unavailable, using mock data for: {q}")
        audit = generate_mock_audit(q)

    return templates.TemplateResponse(
        "partials/audit-results.html",
        {"request": request, "audit": audit},
    )


if __name__ == "__main__":
    import uvicorn

    print("Starting Local SEO Audit Dashboard...")
    print(f"Open http://localhost:{APP_PORT} in your browser")
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
