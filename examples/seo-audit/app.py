#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fastapi>=0.109.0",
#     "uvicorn>=0.27.0",
#     "jinja2>=3.1.0",
#     "python-multipart>=0.0.6",
# ]
# ///
"""
Local SEO Audit Dashboard - Greeble Demo

A demo FastAPI application showcasing the Greeble SEO audit components.
Run with: uv run examples/seo-audit/app.py
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Paths
APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# App setup
app = FastAPI(title="Local SEO Audit Dashboard")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


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
    grade = next(g for threshold, g in sorted(grade_map.items(), reverse=True) if base_score >= threshold)

    # Generate factors
    factors = [
        {"key": "nap_consistency", "label": "NAP Consistency", "weight": 0.40, "value": random.uniform(0.6, 0.95)},
        {"key": "listing_completeness", "label": "Listing Completeness", "weight": 0.25, "value": random.uniform(0.5, 0.9)},
        {"key": "citation_coverage", "label": "Citation Coverage", "weight": 0.25, "value": random.uniform(0.4, 0.85)},
        {"key": "visibility_hint", "label": "Visibility Hint", "weight": 0.10, "value": random.choice([0.5, 1.0])},
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
        forecast.append({
            "month": f"M{i}",
            "min": int(base_traffic + growth * 0.85),
            "expected": int(base_traffic + growth),
            "max": int(base_traffic + growth * 1.15),
        })

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
    for host, name in random.sample(directories, min(len(directories), diagnostics["distinct_hosts"])):
        citations.append({
            "name": brand,
            "url": f"https://{host}/biz/{brand.lower().replace(' ', '-')}",
            "telephone": f"+1 555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address": {"raw": f"{random.randint(100, 999)} Main St, {location}"},
            "_host": host,
            "_jsonld": random.choice([True, False]),
            "_title": f"{brand} - {name}",
        })

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


@app.post("/api/audit", response_class=HTMLResponse)
async def run_audit(request: Request, q: str = Form(...)):
    """Run an audit and return the results partial."""
    if not q.strip():
        return templates.TemplateResponse(
            "partials/empty.html",
            {"request": request, "message": "Please enter a brand or location."},
        )

    audit = generate_mock_audit(q)
    return templates.TemplateResponse(
        "partials/audit-results.html",
        {"request": request, "audit": audit, **audit},
    )


@app.get("/api/audit/{audit_id}", response_class=HTMLResponse)
async def get_audit(request: Request, audit_id: str):
    """Get a specific audit by ID (mock implementation)."""
    audit = generate_mock_audit(audit_id)
    return templates.TemplateResponse(
        "partials/audit-results.html",
        {"request": request, "audit": audit, **audit},
    )


if __name__ == "__main__":
    import uvicorn

    print("Starting Local SEO Audit Dashboard...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
