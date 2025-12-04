# Local SEO Audit Dashboard

A demo FastAPI application showcasing the Greeble SEO audit components.

## Features

- **Score Gauge**: Radial SVG gauge showing health score with grade
- **Forecast Chart**: Server-rendered SVG area chart with min/expected/max bands
- **Factor Breakdown**: Weighted scoring factors with progress bars
- **Metric Grid**: Key diagnostic metrics in a responsive grid
- **Citation List**: Scrollable list of citation sources with NAP data

## Quick Start

```bash
# From the greeble root directory
uv run examples/seo-audit/app.py
```

Then open http://localhost:8000 in your browser.

## Usage

1. Enter a brand name or "Brand in Location" in the search box
2. Click "Run Audit" to generate mock audit data
3. View the dashboard with score, forecast, insights, and citations

## Architecture

```
examples/seo-audit/
├── app.py                    # FastAPI application
├── templates/
│   ├── index.html            # Main dashboard page
│   ├── partials/
│   │   ├── audit-results.html  # HTMX partial for results
│   │   └── empty.html          # Empty state partial
│   └── greeble/              # Component templates
│       ├── score-gauge.partial.html
│       ├── forecast-chart.partial.html
│       ├── factor-breakdown.partial.html
│       ├── metric-grid.partial.html
│       └── citation-list.partial.html
└── static/
    └── greeble/              # Component CSS
        ├── greeble-core.css
        ├── score-gauge.css
        ├── forecast-chart.css
        ├── factor-breakdown.css
        ├── metric-grid.css
        ├── citation-list.css
        └── audit-dashboard.css
```

## HTMX Integration

The dashboard uses HTMX for dynamic updates:

- Form submission triggers `POST /api/audit`
- Results are swapped into `#audit-results`
- Loading indicator shown during request

## Connecting to Real Backend

Replace `generate_mock_audit()` with a call to your Erasmus workflow:

```python
from erasmus import Workflow, Context

@app.post("/api/audit")
async def run_audit(request: Request, q: str = Form(...)):
    # Run Erasmus workflow
    workflow = load_seo_audit_workflow()
    result = await workflow.run(Context(query=q))
    
    return templates.TemplateResponse(
        "partials/audit-results.html",
        {"request": request, "audit": result.to_dict()}
    )
```

## Components Used

| Component | Purpose |
|-----------|---------|
| `score-gauge` | Health score visualization |
| `forecast-chart` | 12-month traffic projection |
| `factor-breakdown` | Score factor explanation |
| `metric-grid` | Diagnostic metrics |
| `citation-list` | Citation sources |
| `audit-dashboard` | Layout and styling |
