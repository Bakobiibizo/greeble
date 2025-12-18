# Citation List

A scrollable list of citation cards showing business NAP (Name, Address, Phone) data from various sources.

## Summary

Displays citations from web scraping with source URLs, contact information, and structured data indicators. Supports HTMX-powered infinite scroll for large datasets.

## Files

- `templates/greeble/citation-list.html` - Static example markup
- `templates/greeble/citation-list.partial.html` - Jinja2 partial for dynamic rendering
- `static/greeble/citation-list.css` - Component styles

## Usage

### Jinja2 Partial

```jinja2
{% set citations = [
    {
        "name": "Acme Restaurant",
        "url": "https://yelp.com/biz/acme",
        "telephone": "+1 555-123-4567",
        "address": {"raw": "123 Main St, San Francisco, CA"},
        "_host": "yelp.com",
        "_jsonld": true
    },
    ...
] %}
{% include "greeble/citation-list.partial.html" with context %}
```

Variables:
- `title` (str, optional): Section title, default "Citations"
- `citations` (list): List of citation objects with:
  - `name` (str): Business name
  - `url` (str): Source URL
  - `telephone` (str, optional): Phone number
  - `address` (dict|str, optional): Address with `raw` key or plain string
  - `_host` (str): Source domain
  - `_jsonld` (bool): Has structured data
  - `_title` (str): Page title (fallback for name)
- `show_count` (bool, optional): Show citation count badge, default True
- `max_height` (str, optional): CSS max-height value

### FastAPI Example

```python
@app.get("/audit/citations")
async def get_citations(request: Request):
    citations = await fetch_citations(brand="Acme")
    return templates.TemplateResponse(
        "greeble/citation-list.partial.html",
        {"request": request, "citations": citations, "max_height": "20rem"}
    )
```

### HTMX Infinite Scroll

Add a load-more trigger at the end of the list:

```html
<div hx-get="/citations?cursor=xyz" 
     hx-trigger="revealed" 
     hx-target="#citation-list-scroll" 
     hx-swap="beforeend">
  <span class="greeble-citation-list__loading">Loading more...</span>
</div>
```

## Variants

| Class | Description |
|-------|-------------|
| `greeble-citation-list--compact` | Reduced max-height and padding |

## Badges

- **JSON-LD**: Green badge indicating structured data present
- **NAP Mismatch**: Yellow badge for inconsistent business data

## Accessibility

- Links open in new tabs with `rel="noopener"`
- Card structure provides semantic grouping
- Scrollable region has visible scrollbar

## Events

None. This is a display-only component.
