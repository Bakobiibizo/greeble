# Score Gauge

A radial gauge component for displaying scores from 0-100 with automatic color coding and grade labels.

## Summary

Server-rendered SVG gauge that displays a score value with visual feedback. Colors automatically adjust based on score thresholds (green ≥70, yellow ≥50, red <50).

## Files

- `templates/greeble/score-gauge.html` - Static example markup
- `templates/greeble/score-gauge.partial.html` - Jinja2 partial for dynamic rendering
- `static/greeble/score-gauge.css` - Component styles

## Usage

### Static HTML

```html
<div class="greeble-score-gauge">
  <div class="greeble-score-gauge__ring">
    <svg viewBox="0 0 120 120" class="greeble-score-gauge__svg">
      <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="12" stroke-linecap="round"/>
      <circle cx="60" cy="60" r="52" fill="none" stroke="#22c55e" stroke-width="12" stroke-linecap="round"
        stroke-dasharray="326.7" stroke-dashoffset="65.34" transform="rotate(-90 60 60)"/>
    </svg>
    <div class="greeble-score-gauge__center">
      <span class="greeble-score-gauge__value">80</span>
      <span class="greeble-score-gauge__grade">Grade B+</span>
    </div>
  </div>
</div>
```

### Jinja2 Partial

```jinja2
{% include "greeble/score-gauge.partial.html" with context %}
```

Variables:
- `score` (int): Score value 0-100
- `grade` (str): Grade label (e.g., "A", "B+", "C")
- `label` (str, optional): Label above the gauge

### FastAPI Example

```python
@app.get("/audit/score")
async def get_score(request: Request):
    score_data = {"score": 78, "grade": "B+", "label": "Health Score"}
    return templates.TemplateResponse(
        "greeble/score-gauge.partial.html",
        {"request": request, **score_data}
    )
```

## Variants

| Class | Description |
|-------|-------------|
| `greeble-score-gauge--small` | 8rem diameter |
| `greeble-score-gauge--large` | 16rem diameter |
| `greeble-score-gauge--success` | Force green color |
| `greeble-score-gauge--warning` | Force yellow color |
| `greeble-score-gauge--danger` | Force red color |

## Accessibility

- Score value is visible text, readable by screen readers
- Grade provides semantic context for the numeric value
- No motion unless `data-animate` attribute is present

## Events

None. This is a display-only component.
