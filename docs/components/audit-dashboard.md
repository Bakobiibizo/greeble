# Audit Dashboard

A composite dashboard component for Local SEO audits, combining score gauge, forecast chart, factor breakdown, diagnostics grid, and citation list.

## Summary

Full-page dashboard layout with HTMX-powered search form. Displays comprehensive audit results including health score, 12-month forecast, AI insights, and citation sources.

## Files

- `templates/greeble/audit-dashboard.html` - Main dashboard shell with search form
- `templates/greeble/audit-dashboard.partial.html` - Results partial for HTMX swap
- `static/greeble/audit-dashboard.css` - Dashboard layout styles

## Dependencies

This component includes the following sub-components:
- `score-gauge` - Health score visualization
- `forecast-chart` - 12-month projection chart
- `factor-breakdown` - Score factor cards
- `metric-grid` - Diagnostics display
- `citation-list` - Citation sources

## Usage

### Main Dashboard

```html
{% include "greeble/audit-dashboard.html" %}
```

### Results Partial (returned by API)

```jinja2
{% set audit = {
    "location": {"brand": "Acme", "location": "San Francisco, CA"},
    "score": {"value": 78, "grade": "B+", "factors": [...], "recommendations": [...]},
    "forecast": [...],
    "diagnostics": {...},
    "citations": [...],
    "insight": "Found 12 citations across 5 domains..."
} %}
{% include "greeble/audit-dashboard.partial.html" with context %}
```

### FastAPI Example

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse("greeble/audit-dashboard.html", {"request": request})

@app.post("/api/audit")
async def run_audit(request: Request, q: str = Form(...)):
    # Run audit workflow
    audit_result = await generate_audit(q)
    return templates.TemplateResponse(
        "greeble/audit-dashboard.partial.html",
        {"request": request, "audit": audit_result}
    )
```

## HTMX Integration

The dashboard uses HTMX for:
- **Form submission**: `hx-post="/api/audit"` triggers audit
- **Results swap**: `hx-target="#audit-results"` replaces content
- **Loading indicator**: `hx-indicator="#audit-loading"` shows spinner

## Layout

```
┌─────────────────────────────────────────────────────┐
│ Header: Title + Search Form                         │
├─────────────────────────────────────────────────────┤
│ Location: Brand + Address + Domain                  │
├──────────────────┬──────────────────────────────────┤
│ Score Gauge      │ Forecast Chart                   │
│ + Recommendations│                                  │
├──────────────────┴──────────────────────────────────┤
│ AI Insight + Factor Breakdown                       │
├─────────────────────────┬───────────────────────────┤
│ Diagnostics Grid        │ Citation List             │
└─────────────────────────┴───────────────────────────┘
```

## Accessibility

- Form has labeled input
- Loading state announced via HTMX
- Semantic heading hierarchy
- All sub-components follow accessibility guidelines

## Events

| Event | Trigger |
|-------|---------|
| `htmx:beforeRequest` | Audit form submitted |
| `htmx:afterSwap` | Results loaded |
