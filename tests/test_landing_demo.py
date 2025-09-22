from __future__ import annotations

import html
import json
import re
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from examples.site import landing


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(landing.app) as test_client:
        yield test_client


def test_modal_flow(client: TestClient) -> None:
    resp = client.get("/modal/example")
    assert resp.status_code == 200
    assert "greeble-modal" in resp.text

    invalid = client.post("/modal/submit", data={"email": ""})
    assert invalid.status_code == 400
    assert "greeble-toast--danger" in invalid.text
    assert "greeble-modal" in invalid.text  # modal stays mounted

    valid = client.post("/modal/submit", data={"email": "demo@example.com"})
    assert valid.status_code == 200
    assert 'id="modal-root"' in valid.text
    assert "greeble-toast--success" in valid.text


def test_newsletter_subscribe_toast(client: TestClient) -> None:
    resp = client.post("/newsletter/subscribe")
    assert resp.status_code == 200
    assert "greeble-toast--info" in resp.text
    assert "launch list" in resp.text


def test_palette_search_and_select(client: TestClient) -> None:
    search = client.post("/palette/search", data={"q": "orbit"})
    assert search.status_code == 200
    assert 'role="option"' in search.text

    detail = client.post("/palette/select", data={"sku": "orbit-kit"})
    assert detail.status_code == 200
    assert "Orbit Collaboration Kit" in detail.text
    assert "Async-friendly" in detail.text


def test_table_pagination_and_sorting(client: TestClient) -> None:
    first_page = client.get("/table", params={"page": 1})
    assert first_page.status_code == 200
    assert "<tr>" in first_page.text
    trigger_header = first_page.headers.get("HX-Trigger")
    assert trigger_header is not None
    assert json.loads(trigger_header) == {"greeble:table:update": {"page": 1, "sort": "org:asc"}}
    body = html.unescape(first_page.text)
    expected_page_one = sorted(landing.ACCOUNTS, key=lambda a: a.org.lower())[:3]
    for account in expected_page_one:
        assert account.org in body

    sorted_desc = client.get("/table", params={"page": 1, "sort": "seats:desc"})
    assert sorted_desc.status_code == 200
    # Highest utilization account should surface first when sorting desc
    sorted_body = html.unescape(sorted_desc.text)
    top_account = max(landing.ACCOUNTS, key=lambda a: a.seats_used / a.seats_total)
    assert top_account.org in sorted_body

    second_page = client.get("/table", params={"page": 2, "sort": "org:asc"})
    assert second_page.status_code == 200
    # Ensure the second page shows different results
    assert second_page.text != first_page.text


def test_table_search_and_actions(client: TestClient) -> None:
    search = client.post("/table/search", data={"q": "nova"})
    assert search.status_code == 200
    assert "Nova Civic" in html.unescape(search.text)

    no_match = client.post("/table/search", data={"q": "zzz"})
    assert no_match.status_code == 200
    assert "No accounts match" in no_match.text

    export = client.post("/table/export")
    assert export.status_code == 200
    assert "greeble-toast" in export.text
    assert json.loads(export.headers["HX-Trigger"]) == {"greeble:toast": {"level": "info"}}

    active_account = next(acc for acc in landing.ACCOUNTS if acc.status == "active")
    view = client.get(f"/table/accounts/{landing._account_slug(active_account)}")
    assert view.status_code == 200
    assert "Account opened" in html.unescape(view.text)
    assert json.loads(view.headers["HX-Trigger"]) == {
        "greeble:table:view": {"org": active_account.org}
    }

    pending_account = next(acc for acc in landing.ACCOUNTS if acc.status == "pending")
    remind = client.post(f"/table/accounts/{landing._account_slug(pending_account)}/remind")
    assert remind.status_code == 200
    assert "Reminder sent" in html.unescape(remind.text)
    assert json.loads(remind.headers["HX-Trigger"]) == {
        "greeble:table:remind": {"org": pending_account.org}
    }

    delinquent_account = next(acc for acc in landing.ACCOUNTS if acc.status == "delinquent")
    escalate = client.post(f"/table/accounts/{landing._account_slug(delinquent_account)}/escalate")
    assert escalate.status_code == 200
    assert "Escalation logged" in html.unescape(escalate.text)
    assert json.loads(escalate.headers["HX-Trigger"]) == {
        "greeble:table:escalate": {"org": delinquent_account.org}
    }

    archive = client.delete(f"/table/accounts/{landing._account_slug(active_account)}")
    assert archive.status_code == 200
    assert "Archived" in html.unescape(archive.text)
    assert json.loads(archive.headers["HX-Trigger"]) == {
        "greeble:table:archive": {"org": active_account.org}
    }

    dismiss = client.get("/toast/dismiss")
    assert dismiss.status_code == 200
    assert dismiss.text == ""


def test_tabs_endpoints(client: TestClient) -> None:
    overview = client.get("/tabs/overview")
    pricing = client.get("/tabs/pricing")
    assert overview.status_code == 200
    assert pricing.status_code == 200
    assert "mission control" in overview.text
    assert "Usage-based pricing" in pricing.text

    missing = client.get("/tabs/missing")
    assert missing.status_code == 404


def test_drawer_open_and_close(client: TestClient) -> None:
    opened = client.get("/drawer/open")
    assert opened.status_code == 200
    assert "drawer-overlay" in opened.text

    closed = client.get("/drawer/close")
    assert closed.status_code == 200
    assert closed.text == ""


def test_sign_in_validation_and_submit(client: TestClient) -> None:
    invalid = client.post("/auth/validate", data={"email": "invalid"})
    assert invalid.status_code == 400
    assert "signin-error" in invalid.text
    assert "aria-invalid" in invalid.text

    valid = client.post("/auth/validate", data={"email": "ok@example.com"})
    assert valid.status_code == 200
    assert "signin-error" not in valid.text

    submit_invalid = client.post("/auth/sign-in", data={"email": ""})
    assert submit_invalid.status_code == 400
    assert "sign-in-status" in submit_invalid.text
    assert "Fix the highlighted field" in submit_invalid.text

    submit_valid = client.post("/auth/sign-in", data={"email": "team@example.com"})
    assert submit_valid.status_code == 200
    assert "greeble-toast--success" in submit_valid.text
    assert "We sent a magic link" in submit_valid.text


def test_infinite_list_sequence(client: TestClient) -> None:
    first_batch = client.get("/list")
    second_batch = client.get("/list")
    assert first_batch.status_code == 200
    assert second_batch.status_code == 200

    pattern = re.compile(r"#(\d+)")
    first_numbers = [int(match) for match in pattern.findall(first_batch.text)]
    second_numbers = [int(match) for match in pattern.findall(second_batch.text)]
    assert max(first_numbers) < min(second_numbers)


def test_sse_stream_emits_oob_fragments(client: TestClient) -> None:
    headers = {"x-test": "1", "accept": "text/event-stream"}
    with client.stream("GET", "/stream", headers=headers, timeout=2.0) as stream:
        assert stream.status_code == 200
        assert "text/event-stream" in stream.headers["content-type"].lower()

        found = False
        for line in stream.iter_lines():
            if not line:
                continue
            text = line.decode() if isinstance(line, bytes) else line
            # first line is ": open", skip it
            if "hx-swap-oob" in text:
                found = True
                break
    assert found
