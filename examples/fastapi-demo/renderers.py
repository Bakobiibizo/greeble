from __future__ import annotations

import json
import textwrap
from collections.abc import Sequence
from typing import Any

from .data import ACCOUNT_STATUS_BADGES, ACCOUNTS, PALETTE_ENTRIES

__all__ = [
    "render_table",
    "render_account_row",
    "render_palette_results",
    "render_palette_detail",
]


Account = dict[str, Any]


def _filter_sort_accounts(sort: str, query: str) -> list[Account]:
    items: list[Account] = list(ACCOUNTS)
    if sort:
        field, _, direction = sort.partition(":")
        reverse = direction.strip().lower() == "desc"

        def key_by_seats(item: Account) -> int:
            used, _ = item["seats"]  # type: ignore[index]
            return used

        def key_by_field(item: Account) -> Any:
            return item.get(field, "")

        key_fn = key_by_seats if field == "seats" else key_by_field
        items.sort(key=key_fn, reverse=reverse)

    if query:
        query_norm = query.lower()
        items = [
            acct
            for acct in items
            if query_norm in acct["org"].lower() or query_norm in acct["owner"].lower()
        ]

    return items


def render_table(page: str = "1", sort: str = "", query: str = "") -> str:
    rows = _filter_sort_accounts(sort, query)
    try:
        page_num = max(int(page), 1)
    except ValueError:
        page_num = 1

    page_size = 3
    start = (page_num - 1) * page_size
    current = rows[start : start + page_size]

    if not current:
        return """<tr><td colspan=5>No accounts match this view.</td></tr>"""

    rendered = [render_account_row(account) for account in current]
    return "\n".join(rendered)


def render_account_row(account: Account) -> str:
    used, cap = account["seats"]  # type: ignore[index]
    badge_class = ACCOUNT_STATUS_BADGES.get(account["status"], "")
    return textwrap.dedent(
        f"""
        <tr>
          <th scope="row">
            <div class="greeble-table__primary">{account["org"]}</div>
            <p class="greeble-table__meta">Owner: {account["owner"]}</p>
          </th>
          <td>{account["plan"]}</td>
          <td>{used} / {cap}</td>
          <td>
            <span class="greeble-table__status {badge_class}">
              <span aria-hidden="true">●</span>
              {account["status"].title()}
            </span>
          </td>
          <td class="greeble-table__actions">
            <button class="greeble-button greeble-button--ghost" type="button" hx-get="/table/{account["slug"]}" hx-target="#table-inspector" hx-swap="innerHTML">View</button>
            <button class="greeble-button greeble-button--ghost" type="button" hx-post="/table/{account["slug"]}/remind" hx-target="closest tr" hx-swap="none">Send reminder</button>
          </td>
        </tr>
        """
    ).strip()


def render_palette_results(
    *, query: str = "", entries: Sequence[dict[str, str]] | None = None
) -> str:
    dataset: Sequence[dict[str, str]] = entries if entries is not None else PALETTE_ENTRIES

    if query:
        q = query.lower()
        dataset = [
            entry
            for entry in dataset
            if q in entry["title"].lower() or q in entry["subtitle"].lower()
        ]

    items = []
    for index, entry in enumerate(dataset):
        payload = json.dumps({"slug": entry["slug"]})
        selected = "true" if index == 0 else "false"
        shortcut = entry.get("shortcut", "")
        shortcut_markup = (
            f'<span class="greeble-palette__result-kbd">{shortcut}</span>' if shortcut else ""
        )
        items.append(
            textwrap.dedent(
                f"""
                <li role="option" data-customer="{entry["slug"]}" aria-selected="{selected}">
                  <button
                    class="greeble-palette__result"
                    type="button"
                    hx-post="/palette/select"
                    hx-target="#palette-detail"
                    hx-swap="innerHTML"
                    hx-vals='{payload}'
                  >
                    <div class="greeble-palette__result-label">
                      <strong>{entry["title"]}</strong>
                      <span>{entry["subtitle"]}</span>
                    </div>
                    {shortcut_markup}
                  </button>
                </li>
                """
            ).strip()
        )

    if not items:
        return '<div class="greeble-palette__detail-empty"><p>No matches found.</p></div>'

    return (
        textwrap.dedent(
            """
        <ul class="greeble-palette__list" role="listbox" aria-label="Customer results">
        """
        )
        + "\n".join(items)
        + "\n</ul>"
    )


def render_palette_detail(slug: str) -> str:
    account = next((acct for acct in ACCOUNTS if acct["slug"] == slug), None)
    if not account:
        return textwrap.dedent(
            """
            <div class="greeble-palette__detail-empty">
              <p>No customer selected.</p>
            </div>
            """
        ).strip()

    used, cap = account["seats"]  # type: ignore[index]
    status_badge = ACCOUNT_STATUS_BADGES.get(account["status"], "")
    return textwrap.dedent(
        f"""
        <div class="stack" style="gap: var(--greeble-spacing-3);">
          <h3 class="greeble-heading-3">{account["org"]}</h3>
          <p><strong>Plan:</strong> {account["plan"]}</p>
          <p><strong>Owner:</strong> {account["owner"]}</p>
          <p><strong>Seats:</strong> {used} of {cap}</p>
          <p>
            <span class="greeble-table__status {status_badge}">
              <span aria-hidden="true">●</span>
              {account["status"].title()}
            </span>
          </p>
          <p>{account["notes"]}</p>
        </div>
        """
    ).strip()
