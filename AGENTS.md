# Greeble Component Development Plan

## Current Status: In Progress

Last updated: 2024-12-04

---

## New Components Needed

### 1. Navigation (nav)
**Purpose:** Top-level navigation bar for category links  
**Status:** 🔴 Not Started

Features:
- Horizontal nav links for main categories
- Active state indicator
- Responsive collapse on mobile
- HTMX-powered page section navigation
- Sticky/fixed positioning option

Files to create:
- `packages/greeble_components/components/nav/templates/nav.html`
- `packages/greeble_components/components/nav/static/nav.css`
- `packages/greeble_components/components/nav/static/nav.js` (optional)
- `packages/greeble_components/components/nav/README.md`

---

### 2. Sidebar
**Purpose:** Vertical sidebar for subcategory/section navigation  
**Status:** 🔴 Not Started

Features:
- Collapsible sections/groups
- Active item highlighting
- Scroll spy integration (optional)
- Works with nav for two-level navigation
- Mobile: slides in as overlay or drawer

Files to create:
- `packages/greeble_components/components/sidebar/templates/sidebar.html`
- `packages/greeble_components/components/sidebar/static/sidebar.css`
- `packages/greeble_components/components/sidebar/static/sidebar.js`
- `packages/greeble_components/components/sidebar/README.md`

---

### 3. Footer
**Purpose:** Page footer with links, branding, and secondary info  
**Status:** 🔴 Not Started

Features:
- Multi-column link groups
- Copyright/branding area
- Social links section
- Newsletter signup integration (reuse form components)
- Responsive stacking on mobile

Files to create:
- `packages/greeble_components/components/footer/templates/footer.html`
- `packages/greeble_components/components/footer/static/footer.css`
- `packages/greeble_components/components/footer/README.md`

---

### 4. Mobile Menu (hamburger-menu)
**Purpose:** Collapsible mobile menu with user profile section  
**Status:** 🔴 Not Started

> Note: Called "hamburger" because the ☰ icon looks like a hamburger (three horizontal lines = bun, patty, bun). Silly name, but it stuck.

Features:
- Toggle button (☰ icon)
- Slide-in or dropdown panel
- User profile/avatar section at top
- Navigation links
- Sign out / settings actions
- Smooth open/close animations
- Focus trap when open

Files to create:
- `packages/greeble_components/components/mobile-menu/templates/mobile-menu.html`
- `packages/greeble_components/components/mobile-menu/templates/mobile-menu.partial.html`
- `packages/greeble_components/components/mobile-menu/static/mobile-menu.css`
- `packages/greeble_components/components/mobile-menu/static/mobile-menu.js`
- `packages/greeble_components/components/mobile-menu/README.md`

---

## Implementation Order

1. **Nav** - Foundation for top navigation
2. **Mobile Menu** - Mobile companion to nav
3. **Sidebar** - Secondary navigation
4. **Footer** - Page completion

---

## Progress Tracker

| Component | Templates | CSS | JS | README | Endpoints | Demo Integration |
|-----------|-----------|-----|-----|--------|-----------|------------------|
| nav | ✅ | ✅ | ✅ | ✅ | N/A | ✅ |
| sidebar | ✅ | ✅ | ✅ | ✅ | N/A | ✅ |
| footer | ✅ | ✅ | N/A | ✅ | N/A | ✅ |
| mobile-menu | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend: ⬜ Not started | 🟡 In progress | ✅ Complete

---

## Integration Plan

Once components are built, update `examples/site/landing.py`:

1. Add nav at top with category links (Auth, Navigation, Data, etc.)
2. Add sidebar on left with component links within each category
3. Add mobile-menu for responsive navigation
4. Add footer at bottom

The landing page layout will change from:
```
[Header]
[Content sections...]
```

To:
```
[Nav - categories]
[Mobile Menu Toggle (responsive)]
┌─────────────┬──────────────────────┐
│ Sidebar     │ Content sections...  │
│ (subcats)   │                      │
└─────────────┴──────────────────────┘
[Footer]
```

---

## Notes

- All components should follow existing Greeble patterns (BEM-style classes, HTMX integration)
- CSS should use existing design tokens from `greeble-core.css`
- Components should be copy-paste ready with minimal configuration
- Mobile-first responsive design

---

## Session Log

### 2024-12-04
- Created AGENTS.md for tracking
- Identified 4 new components needed: nav, sidebar, footer, mobile-menu
- Defined features and file structure for each
- Set implementation order

### 2024-12-04 (continued)
- ✅ Created nav component (templates, CSS, JS, README)
- ✅ Created mobile-menu component (templates, CSS, JS, README)
- ✅ Created sidebar component (templates, CSS, JS, README)
- ✅ Created footer component (templates, CSS, README)
- ✅ Integrated all components into landing.py demo
- ✅ Added mobile menu open/close endpoints
- ✅ Updated page layout with app-layout structure

**Commits:**
- `feat(components): add nav and mobile-menu components`
- `feat(components): add sidebar and footer components`

### 2024-12-04 - SEO Audit Components
Added 6 new components for Local SEO audit dashboards, extracted from hooknladder demo:

- ✅ **score-gauge**: Radial SVG gauge for 0-100 scores with auto color-coding (green ≥70, yellow ≥50, red <50)
- ✅ **forecast-chart**: Server-rendered SVG area chart with min/expected/max forecast bands
- ✅ **factor-breakdown**: Weighted scoring factors displayed as cards with progress bars
- ✅ **metric-grid**: Key-value diagnostic metrics in responsive grid layout
- ✅ **citation-list**: Scrollable list of citation cards with NAP (Name, Address, Phone) data
- ✅ **audit-dashboard**: Composite dashboard combining all above components

**Demo Application:**
- Created `examples/seo-audit/` FastAPI demo app
- HTMX-powered search form with mock audit data generation
- Full dashboard rendering with all components

**Files Created:**
```
packages/greeble_components/components/
├── score-gauge/          (templates/, static/)
├── forecast-chart/       (templates/, static/)
├── factor-breakdown/     (templates/, static/)
├── metric-grid/          (templates/, static/)
├── citation-list/        (templates/, static/)
└── audit-dashboard/      (templates/, static/)

docs/components/
├── score-gauge.md
├── forecast-chart.md
├── factor-breakdown.md
├── metric-grid.md
├── citation-list.md
└── audit-dashboard.md

examples/seo-audit/
├── app.py
├── README.md
├── templates/
└── static/
```

**Updated:** `greeble.manifest.yaml` with all new component definitions

**Next Steps:**
1. Connect to Erasmus backend (replace mock data with real workflow)
2. Extract BrowserScraper and NAP extraction to Erasmus services
3. Add SSE streaming for long-running audits
