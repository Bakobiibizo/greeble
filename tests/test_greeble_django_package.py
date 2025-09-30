from __future__ import annotations

import json
import sys
import types

import django
import pytest
from django.conf import settings
from django.template import Context
from django.test import RequestFactory

if not settings.configured:
    settings.configure(
        SECRET_KEY="test-secret",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
        ],
        MIDDLEWARE=[],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {"context_processors": []},
            }
        ],
        USE_TZ=True,
    )

django.setup()

from packages.adapters.greeble_django import (  # noqa: E402  pylint: disable=wrong-import-position
    GreebleMessagesToToastsMiddleware,
    Pagination,
    build_pagination_links,
    csrf_header,
    csrf_headers_json,
    paginate_sequence,
    pagination_context,
    serialize_headers,
)
from packages.adapters.greeble_django.templatetags import (  # noqa: E402  pylint: disable=wrong-import-position
    greeble_tags,
)


def test_csrf_helpers_return_token() -> None:
    request = RequestFactory().get("/")
    header = csrf_header(request)
    assert header["X-CSRFToken"], "CSRF header should include token"

    payload = json.loads(csrf_headers_json(request))
    assert set(payload) == {"X-CSRFToken"}
    assert payload["X-CSRFToken"], "Serialized JSON should include CSRF token"


@pytest.mark.parametrize(
    "mapping,expected",
    [
        (None, "{}"),
        ({"X-Test": "1"}, '{"X-Test": "1"}'),
    ],
)
def test_serialize_headers(mapping: dict[str, str] | None, expected: str) -> None:
    assert serialize_headers(mapping) == expected


def test_paginate_sequence_with_list_and_generator() -> None:
    pagination = paginate_sequence(list(range(1, 6)), page=2, per_page=2)
    assert list(pagination.items) == [3, 4]
    assert pagination.total == 5
    assert pagination.total_pages == 3
    assert pagination.previous_page == 1
    assert pagination.next_page == 3

    pagination_gen = paginate_sequence(iter(range(7)), page=1, per_page=3)
    assert list(pagination_gen.items) == [0, 1, 2]
    assert pagination_gen.total == 7


def test_build_pagination_links_window_and_nav() -> None:
    links = build_pagination_links(
        "https://example.com/accounts",
        current_page=2,
        total_pages=5,
        query_params={"sort": "plan"},
        window=1,
    )
    assert links[0].label == "Prev"
    assert links[0].is_disabled is False
    numbered = [link for link in links if link.page not in (None, 1, 5)]
    assert any(link.page == 2 and link.is_active for link in numbered)
    assert links[-1].label == "Next"


def test_pagination_context_returns_navigation_urls() -> None:
    pagination = Pagination(items=[1, 2], page=2, per_page=2, total=6)
    context = pagination_context(
        pagination,
        base_url="/table",
        query_params={"sort": "plan"},
        window=1,
    )
    assert context["previous_url"] is not None
    assert context["previous_url"].startswith("/table")
    assert context["next_url"] is not None
    assert context["next_url"].startswith("/table")
    assert any(link.is_active and link.page == 2 for link in context["page_links"])


def test_template_tags_csrf_and_hx_headers() -> None:
    request = RequestFactory().get("/")
    ctx = Context({"request": request})
    csrf_json = greeble_tags.greeble_csrf_headers(ctx)
    assert json.loads(csrf_json)["X-CSRFToken"]

    rendered = greeble_tags.hx_headers({"X-Test": "demo"})
    assert rendered == '{"X-Test": "demo"}'


def test_greeble_pagination_context_tag_uses_request_params() -> None:
    request = RequestFactory().get("/accounts?sort=name&page=3")
    ctx = Context({"request": request})
    pagination = Pagination(items=[1, 2], page=3, per_page=2, total=6)
    tag_context = greeble_tags.greeble_pagination_context(ctx, pagination, window=1)
    assert tag_context["pagination"].page == 3
    assert any(link.is_active and link.page == 3 for link in tag_context["page_links"])


def test_greeble_toast_container_markup_contains_region() -> None:
    markup = greeble_tags.greeble_toast_container()
    assert 'id="greeble-toasts"' in markup


def test_messages_to_toasts_middleware_emits_header(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyMessage:
        level_tag = "success"
        extra_tags = "Saved"

        def __str__(self) -> str:  # pragma: no cover - trivial
            return "All good"

    class DummyResponse:
        def __init__(self) -> None:
            self.headers: dict[str, str] = {"Content-Type": "text/html"}

        def __setitem__(self, key: str, value: str) -> None:
            self.headers[key] = value

    request = object()

    fake_messages = types.SimpleNamespace(get_messages=lambda req: [DummyMessage()])
    original = sys.modules.get("django.contrib.messages")
    monkeypatch.setitem(sys.modules, "django.contrib.messages", fake_messages)

    middleware = GreebleMessagesToToastsMiddleware(lambda _: DummyResponse())
    response = middleware(request)

    payload = json.loads(response.headers["HX-Trigger"])
    assert payload["greeble:toast"][0]["message"] == "All good"

    if original is not None:
        monkeypatch.setitem(sys.modules, "django.contrib.messages", original)
    else:
        monkeypatch.delitem(sys.modules, "django.contrib.messages")
