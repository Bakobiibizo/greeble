from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from html import escape
from pathlib import Path
from string import Template
from typing import Protocol, TypedDict


class ProductLike(Protocol):
    sku: str
    name: str
    tagline: str
    price: float
    inventory: int
    category: str
    description: str


class AccountLike(Protocol):
    org: str
    owner: str
    plan: str
    seats_used: int
    seats_total: int
    status: str


class StepContent(TypedDict, total=False):
    title: str
    description: str
    tasks: Sequence[str]
    prev: str | None
    next: str | None


def load_component_template(components_root: Path, component: str, filename: str) -> str:
    """Read a component template shipped with greeble_components."""
    path = components_root / component / "templates" / filename
    return path.read_text(encoding="utf-8")


def load_component_stylesheets(components_root: Path, assets: Iterable[tuple[str, str]]) -> str:
    """Return a concatenated string of component CSS assets."""
    return "\n".join(
        (components_root / component / "static" / asset).read_text(encoding="utf-8")
        for component, asset in assets
    )


def load_project_component_template(
    project_root: Path, filename: str, *, namespace: str = "greeble"
) -> str:
    """Read a copied component template inside a starter project."""
    base = project_root / "templates"
    if namespace:
        base /= namespace
    return (base / filename).read_text(encoding="utf-8")


def toast_fragment(level: str, title: str, message: str, *, icon: str | None = None) -> str:
    """Build a toast fragment for out-of-band swaps."""
    icons = {
        "success": "✔",
        "info": "ℹ",
        "warn": "!",
        "danger": "✖",
    }
    symbol = icon if icon is not None else icons.get(level, "ℹ")
    return Template(
        """
  <div class="greeble-toast greeble-toast--$level" role="status" data-level="$level">
    <div class="greeble-toast__icon" aria-hidden="true">$icon</div>
    <div class="greeble-toast__body">
      <p class="greeble-toast__title">$title</p>
      <p class="greeble-toast__message">$message</p>
    </div>
  </div>
        """
    ).substitute(
        level=escape(level),
        icon=escape(symbol),
        title=escape(title),
        message=escape(message),
    )


def toast_block(
    toast_html: str, *, container_id: str = "greeble-toasts", swap_oob: bool = True
) -> str:
    """Wrap toast HTML inside a swap container."""
    swap_attr = ' hx-swap-oob="true"' if swap_oob else ""
    return f'<div id="{escape(container_id)}"{swap_attr}>{toast_html}</div>'


def filter_products(products: Iterable[ProductLike], query: str) -> list[ProductLike]:
    """Return products whose metadata contains the query."""
    trimmed = query.strip().lower()
    if not trimmed:
        return list(products)
    results: list[ProductLike] = []
    for product in products:
        haystack = " ".join(
            [
                product.name,
                product.category,
                product.tagline,
                product.description,
            ]
        ).lower()
        if trimmed in haystack:
            results.append(product)
    return results


def render_palette_results(
    products: Iterable[ProductLike],
    *,
    select_url: str = "/palette/select",
    target: str = "#palette-detail",
) -> str:
    """Return palette result markup for the provided products."""
    items: list[str] = []
    for idx, product in enumerate(products):
        selected = "true" if idx == 0 else "false"
        items.append(
            Template(
                """
<li role="option" data-sku="$sku" aria-selected="$selected">
  <button class="greeble-palette__result" type="button"
          hx-post="$url"
          hx-target="$target"
          hx-swap="innerHTML"
          hx-vals='{"sku": "$sku"}'>
    <div class="greeble-palette__result-label">
      <strong>$name</strong>
      <span>$tagline</span>
    </div>
    <span class="greeble-palette__result-kbd">$category</span>
  </button>
</li>
                """
            ).substitute(
                sku=escape(product.sku),
                selected=selected,
                url=escape(select_url),
                target=escape(target),
                name=escape(product.name),
                tagline=escape(product.tagline),
                category=escape(product.category),
            )
        )

    if not items:
        return (
            '<p class="greeble-palette__empty" role="status">'
            "No results. Try a different keyword."
            "</p>"
        )

    return (
        '<ul class="greeble-palette__list" role="listbox" aria-label="Command results">'
        + "".join(items)
        + "</ul>"
    )


def render_palette_detail(product: ProductLike) -> str:
    """Return detail card markup for a selected palette product."""
    return Template(
        """
<article class="greeble-palette__detail-card" data-sku="$sku">
  <header>
    <h3 class="greeble-heading-3">$name</h3>
    <p>$tagline</p>
  </header>
  <dl class="greeble-palette__meta">
    <div><dt>SKU</dt><dd>$sku</dd></div>
    <div><dt>Category</dt><dd>$category</dd></div>
    <div><dt>Price</dt><dd>$price_fmt</dd></div>
    <div><dt>Inventory</dt><dd>$inventory</dd></div>
  </dl>
  <p>$description</p>
</article>
        """
    ).substitute(
        sku=escape(product.sku),
        name=escape(product.name),
        tagline=escape(product.tagline),
        category=escape(product.category),
        price_fmt=f"${product.price:.2f}/seat",
        inventory=product.inventory,
        description=escape(product.description),
    )


def sort_accounts(accounts: Iterable[AccountLike], field: str, direction: str) -> list[AccountLike]:
    key_map = {
        "org": lambda a: a.org.lower(),
        "plan": lambda a: a.plan.lower(),
        "seats": lambda a: a.seats_used / max(1, a.seats_total),
        "status": lambda a: {"active": 0, "pending": 1, "delinquent": 2}.get(a.status, 3),
    }
    key = key_map.get(field, key_map["org"])
    reverse = direction == "desc"
    return sorted(accounts, key=key, reverse=reverse)


def paginate_accounts(
    accounts: Iterable[AccountLike],
    *,
    page: int,
    field: str,
    direction: str,
    page_size: int = 3,
) -> list[AccountLike]:
    safe_page = max(page, 1)
    sorted_accounts = sort_accounts(accounts, field, direction)
    start = (safe_page - 1) * page_size
    end = start + page_size
    return sorted_accounts[start:end]


def account_status_display(account: AccountLike) -> tuple[str, str]:
    labels = {
        "active": ("greeble-table__status--active", "Active"),
        "pending": ("greeble-table__status--pending", "Pending"),
        "delinquent": ("greeble-table__status--delinquent", "Delinquent"),
    }
    return labels.get(account.status, ("", account.status.title()))


def account_slug(account: AccountLike) -> str:
    return account.org.lower().replace(" & ", "-").replace(" ", "-")


def _account_secondary_action(account: AccountLike, slug: str) -> str:
    btn_map = {
        "active": (
            "Remind",
            f"/table/accounts/{slug}/remind",
            "greeble-button--secondary",
        ),
        "pending": (
            "Escalate",
            f"/table/accounts/{slug}/escalate",
            "greeble-button--primary",
        ),
        "delinquent": (
            "Archive",
            f"/table/accounts/{slug}/archive",
            "greeble-button--danger",
        ),
    }
    label, url, variation = btn_map.get(
        account.status,
        ("Archive", f"/table/accounts/{slug}/archive", "greeble-button--danger"),
    )
    return Template(
        """
<button class="greeble-button $variation" type="button"
        hx-post="$url"
        hx-target="#greeble-toasts"
        hx-swap="outerHTML">
  $label
</button>
        """
    ).substitute(
        variation=variation,
        url=escape(url),
        label=escape(label),
    )


def render_account_rows(accounts: Iterable[AccountLike]) -> str:
    rows: list[str] = []
    for account in accounts:
        status_class, status_label = account_status_display(account)
        slug = account_slug(account)
        seats = f"{account.seats_used}/{account.seats_total}"
        secondary_action = _account_secondary_action(account, slug)
        rows.append(
            Template(
                """
<tr>
  <td>
    <div class="greeble-table__primary">
      <strong>$org</strong>
      <span>$plan plan · $seats seats</span>
    </div>
  </td>
  <td>$owner</td>
  <td>
    <span class="greeble-table__status $status_class">$status_label</span>
  </td>
  <td class="greeble-table__actions">
    <button class="greeble-button greeble-button--ghost" type="button"
            hx-get="/table/accounts/$slug"
            hx-target="#table-body"
            hx-swap="none">
      View
    </button>
    $secondary_action
  </td>
</tr>
                """
            ).substitute(
                org=escape(account.org),
                plan=escape(account.plan),
                seats=escape(seats),
                owner=escape(account.owner),
                status_class=status_class,
                status_label=status_label,
                slug=escape(slug),
                secondary_action=secondary_action,
            )
        )
    return "".join(rows)


def table_rows(
    accounts: Iterable[AccountLike],
    *,
    page: int,
    field: str,
    direction: str,
    page_size: int = 3,
) -> str:
    rows = render_account_rows(
        paginate_accounts(
            accounts, page=page, field=field, direction=direction, page_size=page_size
        )
    )
    return rows or ""


def filter_accounts(accounts: Iterable[AccountLike], query: str) -> list[AccountLike]:
    trimmed = query.strip().lower()
    if not trimmed:
        return list(accounts)
    results: list[AccountLike] = []
    for account in accounts:
        haystack = " ".join([account.org, account.owner, account.plan]).lower()
        if trimmed in haystack:
            results.append(account)
    return results


def find_account_by_slug(accounts: Iterable[AccountLike], slug: str) -> AccountLike:
    actual_slug = slug.strip().lower()
    for account in accounts:
        if account_slug(account) == actual_slug:
            return account
    raise LookupError(actual_slug)


def render_feed_items(
    messages: Iterable[str], counter: Iterator[int], *, batch_size: int = 3
) -> str:
    items: list[str] = []
    for message in messages:
        idx = next(counter)
        items.append(
            Template(
                """
<li class="greeble-feed__item">
  <strong>Update #$idx</strong>
  <span>$message</span>
</li>
                """
            ).substitute(idx=idx, message=escape(message))
        )
        if len(items) >= batch_size:
            break
    return "".join(items)


def render_stepper_content(step_key: str, steps: dict[str, StepContent]) -> str:
    data = steps.get(step_key)
    if not data:
        msg = "Unknown step"
        raise KeyError(msg)

    tasks_html = "\n".join(f"    <li>{escape(task)}</li>" for task in data.get("tasks", []))
    actions: list[str] = []
    if prev_key := data.get("prev"):
        actions.append(_stepper_button(prev_key, "Back", primary=False))
    if next_key := data.get("next"):
        actions.append(_stepper_button(next_key, "Continue", primary=True))

    return (
        '<section class="greeble-stepper__content" data-step="{key}">\n'
        '  <h3 class="greeble-heading-3">{title}</h3>\n'
        "  <p>{description}</p>\n"
        '  <ul class="greeble-stepper__tasks">\n{tasks}\n  </ul>\n'
        '  <div class="greeble-stepper__actions">\n{actions}\n  </div>\n'
        "</section>\n"
    ).format(
        key=escape(step_key),
        title=escape(data.get("title", "")),
        description=escape(data.get("description", "")),
        tasks=tasks_html,
        actions="\n".join(actions),
    )


def _stepper_button(target: str, label: str, *, primary: bool) -> str:
    variant = " greeble-button--primary" if primary else ""
    escaped_target = escape(target)
    return (
        f'<button class="greeble-button{variant}" type="button"\n'
        f'        hx-get="/stepper/{escaped_target}"\n'
        f'        hx-target="#stepper-panel"\n'
        f'        hx-swap="innerHTML">\n  {escape(label)}\n</button>'
    )


def render_signin_group(email: str, error: str | None, *, swap_oob: bool) -> str:
    classes = ["greeble-field"]
    if error:
        classes.append("greeble-field--invalid")

    attrs = [
        'id="signin-email-group"',
        f'class="{" ".join(classes)}"',
        'hx-post="/auth/validate"',
        (
            'hx-trigger="change from:#signin-email, keyup delay:500ms '
            'from:#signin-email, blur from:#signin-email"'
        ),
        'hx-target="#signin-email-group"',
        'hx-swap="outerHTML"',
        'hx-include="#signin-email"',
    ]
    if swap_oob:
        attrs.append('hx-swap-oob="true"')

    described_by = ["signin-hint"]
    input_attrs = [
        'id="signin-email"',
        'name="email"',
        'type="email"',
        'class="greeble-input"',
        'autocomplete="email"',
        "required",
    ]
    if email:
        input_attrs.append(f'value="{escape(email, quote=True)}"')
    if error:
        input_attrs.append('aria-invalid="true"')
        described_by.append("signin-error")
    input_attrs.append(f'aria-describedby="{escape(" ".join(described_by), quote=True)}"')

    error_html = (
        f'<p id="signin-error" class="greeble-field__error" role="alert">{escape(error)}</p>'
        if error
        else ""
    )

    return Template(
        """
<div $attrs>
  <label class="greeble-field__label" for="signin-email">Work email</label>
  <input $input_attrs />
  <p id="signin-hint" class="greeble-field__hint">We'll email you a magic link.</p>
  $error_html
</div>
        """
    ).substitute(
        attrs=" ".join(attrs),
        input_attrs=" ".join(input_attrs),
        error_html=error_html,
    )


def render_valid_email_group(email: str, *, swap_oob: bool) -> str:
    attrs = [
        'id="form-email-group"',
        'class="greeble-field"',
        'hx-post="/form/validate"',
        (
            'hx-trigger="change from:#form-email, keyup delay:400ms from:#form-email, '
            'blur from:#form-email"'
        ),
        'hx-target="#form-email-group"',
        'hx-swap="outerHTML"',
        'hx-include="#form-email"',
    ]
    if swap_oob:
        attrs.append('hx-swap-oob="true"')

    value_attr = f'value="{escape(email, quote=True)}"' if email else ""

    return Template(
        """
<div $attrs>
  <label class="greeble-field__label" for="form-email">Work email</label>
  <input class="greeble-input" id="form-email" name="email" type="email"
         autocomplete="email" aria-describedby="form-email-hint" required $value />
  <p class="greeble-field__hint" id="form-email-hint">
    Use your company domain for faster approval.
  </p>
</div>
        """
    ).substitute(attrs=" ".join(attrs), value=value_attr)


def validate_signin_email(email: str) -> str | None:
    if not (value := email.strip()):
        return "Email is required to sign in."
    invalid = "@" not in value or value.startswith("@") or value.endswith("@")
    return "Enter a valid work email address." if invalid else None
