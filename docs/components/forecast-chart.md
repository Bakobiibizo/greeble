# Forecast Chart

A server-rendered SVG area chart for displaying time-series forecasts with min/expected/max confidence bands.

## Summary

Displays 12-month (or any time period) projections with three lines showing minimum, expected, and maximum values. Fully server-rendered with no JavaScript dependencies.

## Files

- `templates/greeble/forecast-chart.html` - Static example markup
- `templates/greeble/forecast-chart.partial.html` - Jinja2 partial for dynamic rendering
- `static/greeble/forecast-chart.css` - Component styles

## Usage

### Jinja2 Partial

```jinja2
{% set forecast = [
    {"month": "M1", "min": 90, "expected": 100, "max": 110},
    {"month": "M2", "min": 95, "expected": 108, "max": 120},
    ...
] %}
{% include "greeble/forecast-chart.partial.html" with context %}
```

Variables:
- `title` (str, optional): Chart title, default "12-Month Forecast"
- `forecast` (list): List of data points with `month`, `min`, `expected`, `max` keys
- `y_min` (int, optional): Y-axis minimum, auto-calculated if not provided
- `y_max` (int, optional): Y-axis maximum, auto-calculated if not provided

### FastAPI Example

```python
@app.get("/audit/forecast")
async def get_forecast(request: Request):
    forecast_data = [
        {"month": f"M{i}", "min": 90 + i*8, "expected": 100 + i*10, "max": 112 + i*12}
        for i in range(1, 13)
    ]
    return templates.TemplateResponse(
        "greeble/forecast-chart.partial.html",
        {"request": request, "forecast": forecast_data, "title": "Traffic Forecast"}
    )
```

## Variants

| Class | Description |
|-------|-------------|
| `greeble-forecast-chart--compact` | Reduced height, no header |

## Color Scheme

- **Min line**: Red (#ef4444) - Lower bound
- **Expected line**: Green (#22c55e) - Primary projection
- **Max line**: Orange (#f97316) - Upper bound

## Accessibility

- Chart data should be supplemented with a data table for screen readers
- Legend uses text labels alongside color indicators
- Consider adding `aria-label` describing the chart purpose

## Events

None. This is a display-only component.
