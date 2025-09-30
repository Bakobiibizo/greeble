from __future__ import annotations

from typing import Any

ACCOUNTS: list[dict[str, Any]] = [
    {
        "slug": "orbit-labs",
        "org": "Orbit Labs",
        "owner": "ava@orbitlabs.dev",
        "plan": "Scale",
        "seats": (42, 50),
        "status": "active",
        "renewal": "2025-12-01",
        "notes": "Shipping real-time collaboration tools for orbital ops teams.",
    },
    {
        "slug": "nova-civic",
        "org": "Nova Civic",
        "owner": "sam@nova.city",
        "plan": "Starter",
        "seats": (8, 10),
        "status": "pending",
        "renewal": "2025-04-18",
        "notes": "GovTech consultancy piloting workflow automation across districts.",
    },
    {
        "slug": "comet-ops",
        "org": "Comet Ops",
        "owner": "lin@cometops.io",
        "plan": "Enterprise",
        "seats": (110, 120),
        "status": "delinquent",
        "renewal": "2025-01-05",
        "notes": "Growth-stage logistics platform with dedicated ops pod onboarding.",
    },
    {
        "slug": "aurora-supply",
        "org": "Aurora Supply",
        "owner": "nina@aurorasupply.ai",
        "plan": "Scale",
        "seats": (67, 80),
        "status": "active",
        "renewal": "2026-03-09",
        "notes": "Procurement insights for clean-energy manufacturers.",
    },
    {
        "slug": "helix-health",
        "org": "Helix Health",
        "owner": "dev@helix.health",
        "plan": "Enterprise",
        "seats": (215, 250),
        "status": "active",
        "renewal": "2025-06-30",
        "notes": "Healthcare provider operating multi-region telemedicine clinics.",
    },
]

ACCOUNT_STATUS_BADGES = {
    "active": "greeble-table__status--active",
    "pending": "greeble-table__status--pending",
    "delinquent": "greeble-table__status--delinquent",
}

PALETTE_ENTRIES: list[dict[str, str]] = [
    {
        "slug": "orbit-labs",
        "title": "Orbit Labs",
        "subtitle": "Scale plan · Owner: ava@orbitlabs.dev",
        "shortcut": "O",
    },
    {
        "slug": "nova-civic",
        "title": "Nova Civic",
        "subtitle": "Starter plan · Owner: sam@nova.city",
        "shortcut": "N",
    },
    {
        "slug": "comet-ops",
        "title": "Comet Ops",
        "subtitle": "Enterprise plan · Owner: lin@cometops.io",
        "shortcut": "C",
    },
    {
        "slug": "aurora-supply",
        "title": "Aurora Supply",
        "subtitle": "Scale plan · Owner: nina@aurorasupply.ai",
        "shortcut": "A",
    },
    {
        "slug": "helix-health",
        "title": "Helix Health",
        "subtitle": "Enterprise plan · Owner: dev@helix.health",
        "shortcut": "H",
    },
]

STEP_CONTENT = {
    "plan": "Clarify launch goals, success metrics, and a cross-team timeline before kickoff.",
    "enable": "Distribute enablement briefs, share escalation paths, and confirm support coverage.",
    "launch": "Monitor real-time metrics, announce status updates, and schedule the retro.",
}

INFINITE_ITEMS = [
    "Capture metrics from HQ dashboards",
    "Dispatch approvals to launch team",
    "Schedule release readiness standup",
    "Publish changelog post to community",
    "Archive closed incidents in root cause DB",
    "Rotate API keys for service providers",
    "Send retro invite to stakeholder mailing list",
]
