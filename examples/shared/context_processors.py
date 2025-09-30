from __future__ import annotations

from typing import Any

from .assets import head_markup


def greeble_assets(request: Any) -> dict[str, str]:  # pragma: no cover - Django hook
    return {"greeble_head_assets": head_markup()}
