# Factor Breakdown

Displays weighted scoring factors as cards with progress bars, useful for explaining how composite scores are calculated.

## Summary

A grid of factor cards showing label, weight percentage, progress bar, and value. Automatically color-codes based on value thresholds (green ≥70%, yellow ≥50%, red <50%).

## Files

- `templates/greeble/factor-breakdown.html` - Static example markup
- `templates/greeble/factor-breakdown.partial.html` - Jinja2 partial for dynamic rendering
- `static/greeble/factor-breakdown.css` - Component styles

## Usage

### Jinja2 Partial

```jinja2
{% set factors = [
    {"key": "nap_consistency", "label": "NAP Consistency", "weight": 0.40, "value": 0.85},
    {"key": "listing_completeness", "label": "Listing Completeness", "weight": 0.25, "value": 0.60},
    {"key": "citation_coverage", "label": "Citation Coverage", "weight": 0.25, "value": 0.75},
    {"key": "visibility_hint", "label": "Visibility Hint", "weight": 0.10, "value": 1.0},
] %}
{% include "greeble/factor-breakdown.partial.html" with context %}
```

Variables:
- `title` (str, optional): Section title, default "Score Breakdown"
- `factors` (list): List of factor objects with:
  - `key` (str): Unique identifier
  - `label` (str): Display name
  - `weight` (float): Weight as decimal (0.4 = 40%)
  - `value` (float): Score as decimal (0.85 = 85%)

### FastAPI Example

```python
@app.get("/audit/factors")
async def get_factors(request: Request):
    factors = [
        {"key": "nap", "label": "NAP Consistency", "weight": 0.4, "value": 0.85},
        {"key": "completeness", "label": "Listing Completeness", "weight": 0.25, "value": 0.6},
    ]
    return templates.TemplateResponse(
        "greeble/factor-breakdown.partial.html",
        {"request": request, "factors": factors}
    )
```

## Variants

| Class | Description |
|-------|-------------|
| `greeble-factor-breakdown--compact` | Smaller cards, tighter spacing |
| `greeble-factor-breakdown--list` | Single-column horizontal layout |

## Accessibility

- Progress bars are visual only; percentage values are displayed as text
- Factor labels provide context for screen readers
- Consider adding `aria-label` to cards for additional context

## Events

None. This is a display-only component.
