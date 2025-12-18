# Metric Grid

A grid of key-value metric cards for displaying diagnostic data, counts, percentages, and status values.

## Summary

Displays metrics in a responsive grid layout with automatic color coding for percentage values. Ideal for dashboards and diagnostic panels.

## Files

- `templates/greeble/metric-grid.html` - Static example markup
- `templates/greeble/metric-grid.partial.html` - Jinja2 partial for dynamic rendering
- `static/greeble/metric-grid.css` - Component styles

## Usage

### Jinja2 Partial

```jinja2
{% set metrics = [
    {"key": "checked", "label": "Checked", "value": 12, "format": "number"},
    {"key": "matched", "label": "Matched", "value": 8, "format": "number"},
    {"key": "nap_consistency", "label": "NAP Consistency", "value": 0.85, "format": "percent"},
    {"key": "coverage", "label": "Citation Coverage", "value": 0.62, "format": "percent"},
] %}
{% include "greeble/metric-grid.partial.html" with context %}
```

Variables:
- `title` (str, optional): Section title, default "Diagnostics"
- `metrics` (list): List of metric objects with:
  - `key` (str): Unique identifier
  - `label` (str): Display name
  - `value` (str|int|float): The value to display
  - `format` (str, optional): `number`, `percent`, or `currency`
  - `color` (str, optional): Force color: `success`, `warning`, `danger`, `muted`
- `columns` (int, optional): Number of columns, default 2

### FastAPI Example

```python
@app.get("/audit/diagnostics")
async def get_diagnostics(request: Request):
    metrics = [
        {"key": "checked", "label": "Checked", "value": 12},
        {"key": "matched", "label": "Matched", "value": 8},
        {"key": "nap", "label": "NAP Consistency", "value": 0.85, "format": "percent"},
    ]
    return templates.TemplateResponse(
        "greeble/metric-grid.partial.html",
        {"request": request, "metrics": metrics, "columns": 3}
    )
```

## Variants

| Class | Description |
|-------|-------------|
| `greeble-metric-grid--compact` | Smaller cards and text |
| `greeble-metric-grid--inline` | Horizontal card layout |

## Accessibility

- Labels use uppercase styling but remain readable
- Values are displayed as plain text for screen readers
- Color is supplemented with the actual value

## Events

None. This is a display-only component.
