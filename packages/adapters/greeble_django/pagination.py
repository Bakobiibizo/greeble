"""
HTMX-aware pagination helpers for Django views.

Purpose:
    Generate HTMX-enabled pagination links and contexts for table components.
Inputs:
    - Query parameters, base URL, page size, total counts.
Outputs:
    - Context objects or HTML strings for pagination controls.
Dependencies:
    - Django URL utilities; HTMX.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from itertools import islice
from typing import Any, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

__all__ = [
    "Pagination",
    "PageLink",
    "paginate_sequence",
    "build_pagination_links",
    "pagination_context",
]


@dataclass(frozen=True, slots=True)
class Pagination:
    """Structure describing a single page of results."""

    items: Sequence[Any]
    page: int
    per_page: int
    total: int

    @property
    def total_pages(self) -> int:
        return max((self.total - 1) // self.per_page + 1, 1)

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def previous_page(self) -> int | None:
        return self.page - 1 if self.has_previous else None

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.has_next else None


@dataclass(frozen=True, slots=True)
class PageLink:
    """Metadata describing a single pagination control link."""

    label: str
    page: int | None
    url: str | None
    is_active: bool = False
    is_disabled: bool = False
    is_ellipsis: bool = False


def paginate_sequence(
    data: Sequence[Any] | Iterable[Any],
    *,
    page: int,
    per_page: int,
    total: int | None = None,
) -> Pagination:
    """Slice an iterable/sequence into a pagination structure."""

    if per_page <= 0:
        raise ValueError("per_page must be positive")

    page = max(1, int(page or 1))
    start = (page - 1) * per_page
    stop = start + per_page

    sequence, materialised = _ensure_sequence(data)
    count = _resolve_total(sequence, total, materialised)
    items = _slice_items(sequence, start, stop)

    return Pagination(items=items, page=page, per_page=per_page, total=count)


def build_pagination_links(
    base_url: str,
    *,
    current_page: int,
    total_pages: int,
    query_params: Mapping[str, str | int | float | None] | None = None,
    page_param: str = "page",
    window: int = 2,
) -> list[PageLink]:
    """Generate navigation links (Prev, numbered pages, Next)."""

    total_pages = max(total_pages, 1)
    current_page = max(1, min(current_page, total_pages))
    params = dict(query_params or {})

    links: list[PageLink] = []

    def _link(page: int, label: str | None = None, *, disabled: bool = False) -> PageLink:
        label = label or str(page)
        url = None if disabled else _build_url(base_url, params, page_param, page)
        return PageLink(
            label=label,
            page=page,
            url=url,
            is_active=(page == current_page),
            is_disabled=disabled,
        )

    links.append(_link(current_page - 1, "Prev", disabled=current_page == 1))

    previous = None
    for number in _windowed_pages(current_page, total_pages, window):
        if previous is not None and number - previous > 1:
            links.append(
                PageLink(label="…", page=None, url=None, is_disabled=True, is_ellipsis=True)
            )
        links.append(_link(number))
        previous = number

    links.append(_link(current_page + 1, "Next", disabled=current_page == total_pages))
    return links


def pagination_context(
    pagination: Pagination,
    *,
    base_url: str,
    query_params: Mapping[str, str | int | float | None] | None = None,
    page_param: str = "page",
    window: int = 2,
) -> dict[str, Any]:
    """Build a template-ready context for pagination controls."""

    params = dict(query_params or {})
    links = build_pagination_links(
        base_url,
        current_page=pagination.page,
        total_pages=pagination.total_pages,
        query_params=params,
        page_param=page_param,
        window=window,
    )

    previous_url = None
    if pagination.previous_page is not None:
        previous_url = _build_url(base_url, params, page_param, pagination.previous_page)

    next_url = None
    if pagination.next_page is not None:
        next_url = _build_url(base_url, params, page_param, pagination.next_page)

    return {
        "pagination": pagination,
        "page_links": links,
        "previous_url": previous_url,
        "next_url": next_url,
    }


def _resolve_total(
    data: Sequence[Any], total: int | None, materialised: Sequence[Any] | None
) -> int:
    if total is not None:
        return max(int(total), 0)

    counter = getattr(data, "count", None)
    if callable(counter):
        with suppress(Exception):
            return max(int(counter()), 0)

    try:
        return max(len(data), 0)
    except TypeError:
        if materialised is not None:
            return len(materialised)
        raise


def _slice_items(data: Sequence[Any], start: int, stop: int) -> list[Any]:
    try:
        return list(data[start:stop])
    except Exception:
        iterator: Iterator[Any] = iter(data)
        return list(islice(iterator, start, stop))


def _windowed_pages(current_page: int, total_pages: int, window: int) -> Iterator[int]:
    window = max(window, 0)
    pages = {1, total_pages}
    pages.update(range(max(1, current_page - window), min(total_pages, current_page + window) + 1))
    yield from sorted(pages)


def _ensure_sequence(
    data: Sequence[Any] | Iterable[Any],
) -> tuple[Sequence[Any], Sequence[Any] | None]:
    if isinstance(data, Sequence) or hasattr(data, "__getitem__"):
        return cast(Sequence[Any], data), None

    materialised = list(data)
    return materialised, materialised


def _build_url(
    base_url: str,
    params: Mapping[str, str | int | float | None],
    page_param: str,
    page: int,
) -> str:
    split = urlsplit(base_url)
    query = dict(parse_qsl(split.query, keep_blank_values=True))
    for key, value in params.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = str(value)
    query[page_param] = str(page)
    new_query = urlencode(query)
    return urlunsplit((split.scheme, split.netloc, split.path, new_query, split.fragment))
