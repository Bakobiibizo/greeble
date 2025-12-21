"""
Greeble Theme Playground

An interactive theme customizer that lets developers configure and preview
Greeble's design tokens in real-time. Inspired by modern component library
playgrounds but designed for Python developers.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from string import Template

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8046))

ROOT = Path(__file__).resolve().parents[2]
CORE_ASSETS = ROOT / "packages" / "greeble_core" / "assets" / "css"
SITE_STATIC = Path(__file__).parent / "static"
SITE_TEMPLATES = Path(__file__).parent / "templates"

app = FastAPI(title="Greeble Theme Playground")

app.mount(
    "/static/greeble",
    StaticFiles(directory=str(CORE_ASSETS)),
    name="greeble-static",
)
app.mount(
    "/static",
    StaticFiles(directory=str(SITE_STATIC)),
    name="site-static",
)

# Component categories for the sidebar
COMPONENT_CATEGORIES = {
    "Inputs": [
        {"id": "button", "name": "Button", "icon": "⬚"},
        {"id": "input", "name": "Input", "icon": "⌨"},
        {"id": "form-validated", "name": "Form", "icon": "📋"},
        {"id": "file-upload", "name": "File Upload", "icon": "📁"},
    ],
    "Feedback": [
        {"id": "toast", "name": "Toast", "icon": "💬"},
        {"id": "modal", "name": "Modal", "icon": "◻"},
        {"id": "drawer", "name": "Drawer", "icon": "☰"},
    ],
    "Navigation": [
        {"id": "tabs", "name": "Tabs", "icon": "⊟"},
        {"id": "dropdown", "name": "Dropdown", "icon": "▼"},
        {"id": "palette", "name": "Command Palette", "icon": "⌘"},
        {"id": "stepper", "name": "Stepper", "icon": "→"},
    ],
    "Data": [
        {"id": "table", "name": "Table", "icon": "▦"},
        {"id": "infinite-list", "name": "Infinite List", "icon": "∞"},
    ],
    "Drag & Drop": [
        {"id": "draggable-card", "name": "Draggable Card", "icon": "✋"},
        {"id": "drop-zone", "name": "Drop Zone", "icon": "⬇"},
    ],
}

# Color palettes - themed for Python developers
COLOR_PALETTES = {
    "midnight": {
        "name": "Midnight",
        "description": "Deep dark theme for late-night coding",
        "background": "#0b0b0c",
        "foreground": "#e8e8ea",
        "muted": "#a0a0a7",
        "accent": "#6aa1ff",
    },
    "terminal": {
        "name": "Terminal",
        "description": "Classic green-on-black terminal vibes",
        "background": "#0a0f0a",
        "foreground": "#00ff41",
        "muted": "#4a7c4a",
        "accent": "#00ff41",
    },
    "solar": {
        "name": "Solar",
        "description": "Warm amber tones inspired by Solarized",
        "background": "#002b36",
        "foreground": "#fdf6e3",
        "muted": "#839496",
        "accent": "#b58900",
    },
    "nord": {
        "name": "Nord",
        "description": "Arctic, bluish-gray color palette",
        "background": "#2e3440",
        "foreground": "#eceff4",
        "muted": "#4c566a",
        "accent": "#88c0d0",
    },
    "monokai": {
        "name": "Monokai",
        "description": "The beloved syntax theme",
        "background": "#272822",
        "foreground": "#f8f8f2",
        "muted": "#75715e",
        "accent": "#f92672",
    },
    "dracula": {
        "name": "Dracula",
        "description": "Dark theme with purple accents",
        "background": "#282a36",
        "foreground": "#f8f8f2",
        "muted": "#6272a4",
        "accent": "#bd93f9",
    },
    "github": {
        "name": "GitHub Dark",
        "description": "GitHub's dark mode palette",
        "background": "#0d1117",
        "foreground": "#c9d1d9",
        "muted": "#8b949e",
        "accent": "#58a6ff",
    },
    "paper": {
        "name": "Paper",
        "description": "Light theme for daylight coders",
        "background": "#fafafa",
        "foreground": "#1a1a1a",
        "muted": "#6b7280",
        "accent": "#2563eb",
    },
}

# Radius presets
RADIUS_PRESETS = {
    "none": {"name": "None", "value": "0"},
    "sm": {"name": "Small", "value": "4px"},
    "md": {"name": "Medium", "value": "8px"},
    "lg": {"name": "Large", "value": "12px"},
    "xl": {"name": "Extra Large", "value": "16px"},
}

# Shadow presets
SHADOW_PRESETS = {
    "none": {"name": "None", "value1": "none", "value2": "none"},
    "subtle": {
        "name": "Subtle",
        "value1": "0 1px 2px rgba(0,0,0,.1)",
        "value2": "0 4px 12px rgba(0,0,0,.15)",
    },
    "medium": {
        "name": "Medium",
        "value1": "0 1px 2px rgba(0,0,0,.2)",
        "value2": "0 8px 30px rgba(0,0,0,.35)",
    },
    "dramatic": {
        "name": "Dramatic",
        "value1": "0 2px 8px rgba(0,0,0,.3)",
        "value2": "0 16px 48px rgba(0,0,0,.5)",
    },
}

# Font presets
FONT_PRESETS = {
    "system": {
        "name": "System",
        "value": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    },
    "mono": {
        "name": "Monospace",
        "value": "'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace",
    },
    "inter": {
        "name": "Inter",
        "value": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    },
    "geist": {
        "name": "Geist",
        "value": "'Geist', -apple-system, BlinkMacSystemFont, sans-serif",
    },
}


def build_sidebar_html() -> str:
    """Build the left sidebar with component categories."""
    categories_html = []
    for category, components in COMPONENT_CATEGORIES.items():
        items = "\n".join(
            f'''<button class="sidebar-item" data-component="{c["id"]}" type="button">
                <span class="sidebar-item__icon">{c["icon"]}</span>
                <span class="sidebar-item__name">{c["name"]}</span>
            </button>'''
            for c in components
        )
        categories_html.append(f"""
        <div class="sidebar-category">
            <h3 class="sidebar-category__title">{category}</h3>
            <div class="sidebar-category__items">
                {items}
            </div>
        </div>
        """)

    return f"""
    <aside class="playground-sidebar playground-sidebar--left">
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <span class="sidebar-logo__icon">◈</span>
                <span class="sidebar-logo__text">Greeble</span>
            </div>
            <span class="sidebar-version">v0.2.0</span>
        </div>
        <nav class="sidebar-nav">
            <div class="sidebar-section">
                <h2 class="sidebar-section__title">Components</h2>
                {"".join(categories_html)}
            </div>
        </nav>
        <div class="sidebar-footer">
            <a href="https://github.com/bakobiibizo/greeble" target="_blank" rel="noreferrer" class="sidebar-link">
                GitHub
            </a>
            <a href="/" class="sidebar-link">
                Docs
            </a>
        </div>
    </aside>
    """


def build_palette_options_html() -> str:
    """Build color palette selection options."""
    options = []
    for key, palette in COLOR_PALETTES.items():
        options.append(f'''
        <button class="palette-option" data-palette="{key}" type="button" title="{palette["description"]}">
            <span class="palette-option__swatch" style="background: {palette["background"]}; border: 2px solid {palette["accent"]};"></span>
            <span class="palette-option__name">{palette["name"]}</span>
        </button>
        ''')
    return "\n".join(options)


def build_radius_options_html() -> str:
    """Build radius preset options."""
    options = []
    for key, preset in RADIUS_PRESETS.items():
        options.append(f'''
        <button class="radius-option" data-radius="{key}" type="button">
            <span class="radius-option__preview" style="border-radius: {preset["value"]};"></span>
            <span class="radius-option__name">{preset["name"]}</span>
        </button>
        ''')
    return "\n".join(options)


def build_shadow_options_html() -> str:
    """Build shadow preset options."""
    options = []
    for key, preset in SHADOW_PRESETS.items():
        options.append(f'''
        <button class="shadow-option" data-shadow="{key}" type="button">
            <span class="shadow-option__name">{preset["name"]}</span>
        </button>
        ''')
    return "\n".join(options)


def build_font_options_html() -> str:
    """Build font preset options."""
    options = []
    for key, preset in FONT_PRESETS.items():
        options.append(f'''
        <button class="font-option" data-font="{key}" type="button">
            <span class="font-option__name">{preset["name"]}</span>
        </button>
        ''')
    return "\n".join(options)


def build_customizer_html() -> str:
    """Build the right sidebar with theme controls."""
    return f"""
    <aside class="playground-sidebar playground-sidebar--right">
        <div class="customizer-header">
            <h2 class="customizer-title">Theme</h2>
            <div class="customizer-actions">
                <button class="customizer-action" id="randomize-btn" type="button" title="Try random">
                    <span>⚄</span>
                </button>
                <button class="customizer-action" id="reset-btn" type="button" title="Reset">
                    <span>↺</span>
                </button>
            </div>
        </div>

        <div class="customizer-scroll">
            <div class="customizer-section">
                <h3 class="customizer-section__title">Color Palette</h3>
                <div class="palette-grid">
                    {build_palette_options_html()}
                </div>
            </div>

            <div class="customizer-section">
                <h3 class="customizer-section__title">Accent Color</h3>
                <div class="color-picker-row">
                    <input type="color" id="accent-color" class="color-picker" value="#6aa1ff">
                    <input type="text" id="accent-color-text" class="color-text-input" value="#6aa1ff" maxlength="7">
                </div>
            </div>

            <div class="customizer-section">
                <h3 class="customizer-section__title">Border Radius</h3>
                <div class="option-row">
                    {build_radius_options_html()}
                </div>
            </div>

            <div class="customizer-section">
                <h3 class="customizer-section__title">Shadows</h3>
                <div class="option-row">
                    {build_shadow_options_html()}
                </div>
            </div>

            <div class="customizer-section">
                <h3 class="customizer-section__title">Font</h3>
                <div class="option-row option-row--vertical">
                    {build_font_options_html()}
                </div>
            </div>

            <div class="customizer-section">
                <h3 class="customizer-section__title">Spacing</h3>
                <div class="slider-row">
                    <input type="range" id="spacing-scale" class="slider" min="0.5" max="1.5" step="0.1" value="1">
                    <span class="slider-value" id="spacing-value">1x</span>
                </div>
            </div>
        </div>

        <div class="customizer-footer">
            <button class="export-btn" id="export-css-btn" type="button">
                <span class="export-btn__icon">{{ }}</span>
                <span>Export CSS</span>
            </button>
            <button class="export-btn export-btn--secondary" id="copy-vars-btn" type="button">
                <span class="export-btn__icon">📋</span>
                <span>Copy Variables</span>
            </button>
        </div>
    </aside>
    """


def build_preview_blocks_html() -> str:
    """Build the center preview area with component blocks."""
    return """
    <main class="playground-main">
        <div class="preview-header">
            <h1 class="preview-title">Theme Playground</h1>
            <p class="preview-subtitle">Customize your Greeble theme and see changes in real-time</p>
        </div>

        <div class="preview-grid">
            <!-- Card Block -->
            <section class="preview-block" data-block="card">
                <span class="preview-block__label">Card</span>
                <div class="greeble-card preview-card">
                    <div class="preview-card__header">
                        <h3 class="greeble-heading-3">Project Dashboard</h3>
                        <button class="greeble-button greeble-button--ghost" type="button">⋯</button>
                    </div>
                    <p class="preview-card__description">Track your Python projects and deployments in real-time.</p>
                    <div class="preview-card__stats">
                        <div class="preview-stat">
                            <span class="preview-stat__value">12</span>
                            <span class="preview-stat__label">Active</span>
                        </div>
                        <div class="preview-stat">
                            <span class="preview-stat__value">847</span>
                            <span class="preview-stat__label">Requests</span>
                        </div>
                        <div class="preview-stat">
                            <span class="preview-stat__value">99.9%</span>
                            <span class="preview-stat__label">Uptime</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Form Block -->
            <section class="preview-block" data-block="form">
                <span class="preview-block__label">Form</span>
                <div class="greeble-card preview-form">
                    <h3 class="greeble-heading-3">Create Project</h3>
                    <p class="preview-form__description">Set up a new Python project</p>
                    <form class="preview-form__fields">
                        <div class="form-group">
                            <label class="form-label" for="project-name">Project Name</label>
                            <input type="text" id="project-name" class="greeble-input" placeholder="my-python-app">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="framework">Framework</label>
                            <select id="framework" class="greeble-input greeble-select">
                                <option value="">Select framework</option>
                                <option value="fastapi">FastAPI</option>
                                <option value="django">Django</option>
                                <option value="flask">Flask</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="description">Description</label>
                            <textarea id="description" class="greeble-input greeble-textarea" placeholder="Brief project description..." rows="3"></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="greeble-button greeble-button--primary">Create Project</button>
                            <button type="button" class="greeble-button greeble-button--ghost">Cancel</button>
                        </div>
                    </form>
                </div>
            </section>

            <!-- Buttons Block -->
            <section class="preview-block" data-block="buttons">
                <span class="preview-block__label">Buttons</span>
                <div class="greeble-card preview-buttons">
                    <h4 class="preview-buttons__title">Button Variants</h4>
                    <div class="button-row">
                        <button class="greeble-button greeble-button--primary" type="button">Primary</button>
                        <button class="greeble-button greeble-button--secondary" type="button">Secondary</button>
                        <button class="greeble-button greeble-button--ghost" type="button">Ghost</button>
                        <button class="greeble-button greeble-button--destructive" type="button">Destructive</button>
                    </div>
                    <h4 class="preview-buttons__title">States</h4>
                    <div class="button-row">
                        <button class="greeble-button greeble-button--primary" type="button" disabled>Disabled</button>
                        <button class="greeble-button greeble-button--primary greeble-button--loading" type="button">
                            <span class="spinner"></span>
                            Loading
                        </button>
                    </div>
                </div>
            </section>

            <!-- Toast Block -->
            <section class="preview-block" data-block="toast">
                <span class="preview-block__label">Toast</span>
                <div class="preview-toasts">
                    <div class="greeble-toast greeble-toast--success">
                        <span class="greeble-toast__icon">✓</span>
                        <div class="greeble-toast__content">
                            <strong class="greeble-toast__title">Deployment Complete</strong>
                            <p class="greeble-toast__message">Your app is now live at api.example.com</p>
                        </div>
                    </div>
                    <div class="greeble-toast greeble-toast--info">
                        <span class="greeble-toast__icon">ℹ</span>
                        <div class="greeble-toast__content">
                            <strong class="greeble-toast__title">Build Started</strong>
                            <p class="greeble-toast__message">Running pytest and type checks...</p>
                        </div>
                    </div>
                    <div class="greeble-toast greeble-toast--warning">
                        <span class="greeble-toast__icon">⚠</span>
                        <div class="greeble-toast__content">
                            <strong class="greeble-toast__title">Rate Limited</strong>
                            <p class="greeble-toast__message">Approaching API quota limit</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Table Block -->
            <section class="preview-block preview-block--wide" data-block="table">
                <span class="preview-block__label">Table</span>
                <div class="greeble-card preview-table-wrap">
                    <div class="preview-table-header">
                        <h3 class="greeble-heading-3">Dependencies</h3>
                        <input type="text" class="greeble-input greeble-input--search" placeholder="Search packages...">
                    </div>
                    <table class="greeble-table">
                        <thead>
                            <tr>
                                <th>Package</th>
                                <th>Version</th>
                                <th>Status</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><code>fastapi</code></td>
                                <td>0.109.0</td>
                                <td><span class="status-badge status-badge--success">Latest</span></td>
                                <td><button class="greeble-button greeble-button--ghost greeble-button--sm">Update</button></td>
                            </tr>
                            <tr>
                                <td><code>pydantic</code></td>
                                <td>2.5.3</td>
                                <td><span class="status-badge status-badge--warning">Update Available</span></td>
                                <td><button class="greeble-button greeble-button--ghost greeble-button--sm">Update</button></td>
                            </tr>
                            <tr>
                                <td><code>uvicorn</code></td>
                                <td>0.27.0</td>
                                <td><span class="status-badge status-badge--success">Latest</span></td>
                                <td><button class="greeble-button greeble-button--ghost greeble-button--sm">Update</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Tabs Block -->
            <section class="preview-block" data-block="tabs">
                <span class="preview-block__label">Tabs</span>
                <div class="greeble-card preview-tabs-wrap">
                    <div class="greeble-tabs">
                        <div class="greeble-tabs__list" role="tablist">
                            <button class="greeble-tabs__tab" role="tab" data-active="true">Overview</button>
                            <button class="greeble-tabs__tab" role="tab">Metrics</button>
                            <button class="greeble-tabs__tab" role="tab">Logs</button>
                            <button class="greeble-tabs__tab" role="tab">Settings</button>
                        </div>
                        <div class="greeble-tabs__panel">
                            <p>Application overview and quick stats for your deployment.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Modal Trigger Block -->
            <section class="preview-block" data-block="modal">
                <span class="preview-block__label">Modal</span>
                <div class="greeble-card preview-modal-wrap">
                    <p>Dialogs for confirmations and focused workflows</p>
                    <button class="greeble-button greeble-button--primary" type="button" id="preview-modal-trigger">
                        Open Modal
                    </button>
                </div>
            </section>

            <!-- Input Variants Block -->
            <section class="preview-block" data-block="inputs">
                <span class="preview-block__label">Inputs</span>
                <div class="greeble-card preview-inputs">
                    <div class="form-group">
                        <label class="form-label">Default</label>
                        <input type="text" class="greeble-input" placeholder="Enter value...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">With Icon</label>
                        <div class="input-with-icon">
                            <span class="input-icon">🔍</span>
                            <input type="text" class="greeble-input" placeholder="Search...">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Error State</label>
                        <input type="text" class="greeble-input greeble-input--error" value="invalid@">
                        <span class="input-error-text">Please enter a valid email address</span>
                    </div>
                    <div class="form-group">
                        <label class="greeble-checkbox">
                            <input type="checkbox" class="greeble-checkbox__input" checked>
                            <span class="greeble-checkbox__label">Enable notifications</span>
                        </label>
                    </div>
                </div>
            </section>
        </div>

        <!-- Code Output Panel -->
        <section class="code-output">
            <div class="code-output__header">
                <h3 class="code-output__title">Generated CSS Variables</h3>
                <button class="greeble-button greeble-button--ghost greeble-button--sm" id="copy-code-btn" type="button">
                    Copy
                </button>
            </div>
            <pre class="code-output__code" id="css-output"><code>:root {
  --greeble-color-background: #0b0b0c;
  --greeble-color-foreground: #e8e8ea;
  --greeble-color-muted: #a0a0a7;
  --greeble-color-accent: #6aa1ff;
  --greeble-radius-medium: 12px;
  --greeble-shadow-1: 0 1px 2px rgba(0,0,0,.2);
  --greeble-shadow-2: 0 8px 30px rgba(0,0,0,.35);
}</code></pre>
        </section>
    </main>

    <!-- Modal Preview -->
    <div class="modal-preview" id="preview-modal" hidden>
        <div class="greeble-modal__backdrop" data-close-modal></div>
        <div class="greeble-modal__panel">
            <div class="modal-preview__header">
                <h3 class="greeble-heading-3">Confirm Action</h3>
                <button class="greeble-icon-button" type="button" data-close-modal>×</button>
            </div>
            <p>Are you sure you want to deploy this application to production?</p>
            <div class="modal-preview__actions">
                <button class="greeble-button greeble-button--primary" type="button" data-close-modal>Deploy</button>
                <button class="greeble-button greeble-button--ghost" type="button" data-close-modal>Cancel</button>
            </div>
        </div>
    </div>
    """


def build_javascript() -> str:
    """Build the JavaScript for real-time theme customization."""
    palettes_json = json.dumps(COLOR_PALETTES)
    radius_json = json.dumps(RADIUS_PRESETS)
    shadow_json = json.dumps(SHADOW_PRESETS)
    font_json = json.dumps(FONT_PRESETS)

    # Use string.Template to avoid f-string issues with JavaScript template literals
    js_template = Template(r"""
    <script>
    (function() {
        const PALETTES = $palettes_json;
        const RADIUS = $radius_json;
        const SHADOWS = $shadow_json;
        const FONTS = $font_json;

        let currentTheme = {
            palette: 'midnight',
            accentColor: '#6aa1ff',
            radius: 'lg',
            shadow: 'medium',
            font: 'system',
            spacingScale: 1
        };

        function updateCSSVariables() {
            const root = document.documentElement;
            const palette = PALETTES[currentTheme.palette];

            root.style.setProperty('--greeble-color-background', palette.background);
            root.style.setProperty('--greeble-color-foreground', palette.foreground);
            root.style.setProperty('--greeble-color-muted', palette.muted);
            root.style.setProperty('--greeble-color-accent', currentTheme.accentColor);

            const radius = RADIUS[currentTheme.radius];
            root.style.setProperty('--greeble-radius-medium', radius.value);

            const shadow = SHADOWS[currentTheme.shadow];
            root.style.setProperty('--greeble-shadow-1', shadow.value1);
            root.style.setProperty('--greeble-shadow-2', shadow.value2);

            const font = FONTS[currentTheme.font];
            root.style.setProperty('--greeble-font-family', font.value);

            const scale = currentTheme.spacingScale;
            root.style.setProperty('--greeble-spacing-1', (0.25 * scale) + 'rem');
            root.style.setProperty('--greeble-spacing-2', (0.5 * scale) + 'rem');
            root.style.setProperty('--greeble-spacing-3', (0.75 * scale) + 'rem');
            root.style.setProperty('--greeble-spacing-4', (1 * scale) + 'rem');

            updateCodeOutput();
            updateActiveStates();
        }

        function updateCodeOutput() {
            const palette = PALETTES[currentTheme.palette];
            const radius = RADIUS[currentTheme.radius];
            const shadow = SHADOWS[currentTheme.shadow];
            const font = FONTS[currentTheme.font];
            const scale = currentTheme.spacingScale;

            const css = `:root {
  /* Colors */
  --greeble-color-background: $${palette.background};
  --greeble-color-foreground: $${palette.foreground};
  --greeble-color-muted: $${palette.muted};
  --greeble-color-accent: $${currentTheme.accentColor};

  /* Radius */
  --greeble-radius-medium: $${radius.value};

  /* Shadows */
  --greeble-shadow-1: $${shadow.value1};
  --greeble-shadow-2: $${shadow.value2};

  /* Spacing (scale: $${scale}x) */
  --greeble-spacing-1: $${(0.25 * scale).toFixed(3)}rem;
  --greeble-spacing-2: $${(0.5 * scale).toFixed(3)}rem;
  --greeble-spacing-3: $${(0.75 * scale).toFixed(3)}rem;
  --greeble-spacing-4: $${(1 * scale).toFixed(3)}rem;

  /* Font */
  --greeble-font-family: $${font.value};

  /* Focus */
  --greeble-focus-ring: 0 0 0 3px $${currentTheme.accentColor}80;
}`;

            const codeEl = document.querySelector('#css-output code');
            if (codeEl) codeEl.textContent = css;
        }

        function updateActiveStates() {
            // Palette options
            document.querySelectorAll('.palette-option').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.palette === currentTheme.palette);
            });

            // Radius options
            document.querySelectorAll('.radius-option').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.radius === currentTheme.radius);
            });

            // Shadow options
            document.querySelectorAll('.shadow-option').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.shadow === currentTheme.shadow);
            });

            // Font options
            document.querySelectorAll('.font-option').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.font === currentTheme.font);
            });

            // Color pickers
            document.getElementById('accent-color').value = currentTheme.accentColor;
            document.getElementById('accent-color-text').value = currentTheme.accentColor;

            // Spacing slider
            document.getElementById('spacing-scale').value = currentTheme.spacingScale;
            document.getElementById('spacing-value').textContent = currentTheme.spacingScale + 'x';
        }

        function randomizeTheme() {
            const paletteKeys = Object.keys(PALETTES);
            const radiusKeys = Object.keys(RADIUS);
            const shadowKeys = Object.keys(SHADOWS);
            const fontKeys = Object.keys(FONTS);

            currentTheme = {
                palette: paletteKeys[Math.floor(Math.random() * paletteKeys.length)],
                accentColor: '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0'),
                radius: radiusKeys[Math.floor(Math.random() * radiusKeys.length)],
                shadow: shadowKeys[Math.floor(Math.random() * shadowKeys.length)],
                font: fontKeys[Math.floor(Math.random() * fontKeys.length)],
                spacingScale: Math.round((0.5 + Math.random()) * 10) / 10
            };

            updateCSSVariables();
        }

        function resetTheme() {
            currentTheme = {
                palette: 'midnight',
                accentColor: '#6aa1ff',
                radius: 'lg',
                shadow: 'medium',
                font: 'system',
                spacingScale: 1
            };
            updateCSSVariables();
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('Copied to clipboard!');
            });
        }

        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'copy-toast';
            toast.textContent = message;
            document.body.appendChild(toast);

            requestAnimationFrame(() => {
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                    setTimeout(() => toast.remove(), 300);
                }, 2000);
            });
        }

        function exportCSS() {
            const codeEl = document.querySelector('#css-output code');
            if (codeEl) {
                const css = codeEl.textContent;
                const blob = new Blob([css], { type: 'text/css' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'greeble-theme.css';
                a.click();
                URL.revokeObjectURL(url);
                showToast('Theme exported!');
            }
        }

        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            // Palette selection
            document.querySelectorAll('.palette-option').forEach(btn => {
                btn.addEventListener('click', () => {
                    currentTheme.palette = btn.dataset.palette;
                    currentTheme.accentColor = PALETTES[btn.dataset.palette].accent;
                    updateCSSVariables();
                });
            });

            // Radius selection
            document.querySelectorAll('.radius-option').forEach(btn => {
                btn.addEventListener('click', () => {
                    currentTheme.radius = btn.dataset.radius;
                    updateCSSVariables();
                });
            });

            // Shadow selection
            document.querySelectorAll('.shadow-option').forEach(btn => {
                btn.addEventListener('click', () => {
                    currentTheme.shadow = btn.dataset.shadow;
                    updateCSSVariables();
                });
            });

            // Font selection
            document.querySelectorAll('.font-option').forEach(btn => {
                btn.addEventListener('click', () => {
                    currentTheme.font = btn.dataset.font;
                    updateCSSVariables();
                });
            });

            // Accent color picker
            document.getElementById('accent-color').addEventListener('input', (e) => {
                currentTheme.accentColor = e.target.value;
                updateCSSVariables();
            });

            document.getElementById('accent-color-text').addEventListener('change', (e) => {
                if (/^#[0-9A-Fa-f]{6}$$/.test(e.target.value)) {
                    currentTheme.accentColor = e.target.value;
                    updateCSSVariables();
                }
            });

            // Spacing slider
            document.getElementById('spacing-scale').addEventListener('input', (e) => {
                currentTheme.spacingScale = parseFloat(e.target.value);
                updateCSSVariables();
            });

            // Action buttons
            document.getElementById('randomize-btn').addEventListener('click', randomizeTheme);
            document.getElementById('reset-btn').addEventListener('click', resetTheme);
            document.getElementById('export-css-btn').addEventListener('click', exportCSS);
            document.getElementById('copy-vars-btn').addEventListener('click', () => {
                const codeEl = document.querySelector('#css-output code');
                if (codeEl) copyToClipboard(codeEl.textContent);
            });
            document.getElementById('copy-code-btn').addEventListener('click', () => {
                const codeEl = document.querySelector('#css-output code');
                if (codeEl) copyToClipboard(codeEl.textContent);
            });

            // Modal
            const modal = document.getElementById('preview-modal');
            document.getElementById('preview-modal-trigger').addEventListener('click', () => {
                modal.hidden = false;
            });
            modal.querySelectorAll('[data-close-modal]').forEach(el => {
                el.addEventListener('click', () => {
                    modal.hidden = true;
                });
            });

            // Tab interaction
            document.querySelectorAll('.greeble-tabs__tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    document.querySelectorAll('.greeble-tabs__tab').forEach(t => {
                        t.removeAttribute('data-active');
                    });
                    tab.setAttribute('data-active', 'true');
                });
            });

            // Sidebar component navigation
            const componentBlockMap = {
                'button': 'buttons',
                'input': 'inputs',
                'form-validated': 'form',
                'file-upload': 'form',
                'toast': 'toast',
                'modal': 'modal',
                'drawer': 'modal',
                'tabs': 'tabs',
                'dropdown': 'buttons',
                'palette': 'form',
                'stepper': 'tabs',
                'table': 'table',
                'infinite-list': 'table',
                'draggable-card': 'card',
                'drop-zone': 'card'
            };

            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.addEventListener('click', () => {
                    const componentId = item.dataset.component;
                    const blockId = componentBlockMap[componentId] || 'card';
                    const block = document.querySelector(`[data-block="${blockId}"]`);

                    // Remove active from all items, add to clicked
                    document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');

                    if (block) {
                        block.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        // Brief highlight effect
                        block.style.outline = '2px solid var(--greeble-color-accent)';
                        block.style.outlineOffset = '4px';
                        setTimeout(() => {
                            block.style.outline = '';
                            block.style.outlineOffset = '';
                        }, 1500);
                    }
                });
            });

            // Initialize
            updateCSSVariables();
        });
    })();
    </script>
    """)

    return js_template.substitute(
        palettes_json=palettes_json,
        radius_json=radius_json,
        shadow_json=shadow_json,
        font_json=font_json,
    )


def build_styles() -> str:
    """Build the custom styles for the playground."""
    return """
    <style>
    /* Playground Layout */
    * { box-sizing: border-box; }

    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        font-family: var(--greeble-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
    }

    .playground {
        display: grid;
        grid-template-columns: 240px 1fr 300px;
        min-height: 100vh;
        background: var(--greeble-color-background);
        color: var(--greeble-color-foreground);
    }

    @media (max-width: 1200px) {
        .playground {
            grid-template-columns: 200px 1fr 260px;
        }
    }

    @media (max-width: 900px) {
        .playground {
            grid-template-columns: 1fr;
        }
        .playground-sidebar--left {
            display: none;
        }
        .playground-sidebar--right {
            position: fixed;
            right: 0;
            top: 0;
            bottom: 0;
            z-index: 100;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        .playground-sidebar--right.open {
            transform: translateX(0);
        }
    }

    /* Sidebar Styles */
    .playground-sidebar {
        background: rgba(0, 0, 0, 0.3);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        flex-direction: column;
        height: 100vh;
        position: sticky;
        top: 0;
    }

    .playground-sidebar--right {
        border-right: none;
        border-left: 1px solid rgba(255, 255, 255, 0.08);
    }

    .sidebar-header {
        padding: 1.25rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        font-size: 1.1rem;
    }

    .sidebar-logo__icon {
        color: var(--greeble-color-accent);
        font-size: 1.4rem;
    }

    .sidebar-version {
        font-size: 0.75rem;
        color: var(--greeble-color-muted);
        background: rgba(255, 255, 255, 0.06);
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
    }

    .sidebar-nav {
        flex: 1;
        overflow-y: auto;
        padding: 1rem 0;
    }

    .sidebar-section__title {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--greeble-color-muted);
        padding: 0.5rem 1rem;
        margin: 0;
    }

    .sidebar-category {
        margin-bottom: 0.5rem;
    }

    .sidebar-category__title {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--greeble-color-muted);
        padding: 0.5rem 1rem;
        margin: 0;
    }

    .sidebar-category__items {
        display: flex;
        flex-direction: column;
    }

    .sidebar-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 1rem;
        background: none;
        border: none;
        color: var(--greeble-color-foreground);
        cursor: pointer;
        text-align: left;
        font-size: 0.875rem;
        transition: background 0.15s, color 0.15s;
    }

    .sidebar-item:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .sidebar-item.active {
        background: color-mix(in srgb, var(--greeble-color-accent) 15%, transparent);
        color: var(--greeble-color-accent);
    }

    .sidebar-item__icon {
        width: 1.25rem;
        text-align: center;
        opacity: 0.7;
    }

    .sidebar-footer {
        padding: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        gap: 1rem;
    }

    .sidebar-link {
        font-size: 0.8rem;
        color: var(--greeble-color-muted);
        text-decoration: none;
    }

    .sidebar-link:hover {
        color: var(--greeble-color-accent);
    }

    /* Customizer Styles */
    .customizer-header {
        padding: 1.25rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .customizer-title {
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }

    .customizer-actions {
        display: flex;
        gap: 0.25rem;
    }

    .customizer-action {
        background: none;
        border: none;
        color: var(--greeble-color-muted);
        cursor: pointer;
        padding: 0.35rem;
        border-radius: 4px;
        font-size: 1rem;
        transition: background 0.15s, color 0.15s;
    }

    .customizer-action:hover {
        background: rgba(255, 255, 255, 0.08);
        color: var(--greeble-color-foreground);
    }

    .customizer-scroll {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
    }

    .customizer-section {
        margin-bottom: 1.5rem;
    }

    .customizer-section__title {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--greeble-color-muted);
        margin: 0 0 0.75rem 0;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Palette Grid */
    .palette-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
    }

    .palette-option {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid transparent;
        border-radius: var(--greeble-radius-medium, 8px);
        cursor: pointer;
        color: var(--greeble-color-foreground);
        font-size: 0.8rem;
        transition: border-color 0.15s, background 0.15s;
    }

    .palette-option:hover {
        background: rgba(255, 255, 255, 0.06);
    }

    .palette-option.active {
        border-color: var(--greeble-color-accent);
        background: rgba(255, 255, 255, 0.05);
    }

    .palette-option__swatch {
        width: 1.25rem;
        height: 1.25rem;
        border-radius: 4px;
        flex-shrink: 0;
    }

    .palette-option__name {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Color Picker */
    .color-picker-row {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .color-picker {
        width: 3rem;
        height: 2rem;
        padding: 0;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        background: none;
    }

    .color-picker::-webkit-color-swatch-wrapper {
        padding: 0;
    }

    .color-picker::-webkit-color-swatch {
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .color-text-input {
        flex: 1;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 0.4rem 0.6rem;
        color: var(--greeble-color-foreground);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }

    /* Option Rows */
    .option-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
    }

    .option-row--vertical {
        flex-direction: column;
    }

    .radius-option,
    .shadow-option,
    .font-option {
        padding: 0.4rem 0.6rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid transparent;
        border-radius: 4px;
        cursor: pointer;
        color: var(--greeble-color-foreground);
        font-size: 0.75rem;
        transition: border-color 0.15s, background 0.15s;
    }

    .radius-option:hover,
    .shadow-option:hover,
    .font-option:hover {
        background: rgba(255, 255, 255, 0.06);
    }

    .radius-option.active,
    .shadow-option.active,
    .font-option.active {
        border-color: var(--greeble-color-accent);
        background: rgba(255, 255, 255, 0.05);
    }

    .radius-option {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .radius-option__preview {
        width: 1rem;
        height: 1rem;
        border: 2px solid var(--greeble-color-accent);
        background: transparent;
    }

    .font-option {
        width: 100%;
        text-align: left;
    }

    /* Slider */
    .slider-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .slider {
        flex: 1;
        height: 4px;
        appearance: none;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
        cursor: pointer;
    }

    .slider::-webkit-slider-thumb {
        appearance: none;
        width: 14px;
        height: 14px;
        background: var(--greeble-color-accent);
        border-radius: 50%;
        cursor: pointer;
    }

    .slider-value {
        font-size: 0.8rem;
        color: var(--greeble-color-muted);
        min-width: 2rem;
    }

    /* Customizer Footer */
    .customizer-footer {
        padding: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .export-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.6rem 1rem;
        background: var(--greeble-color-accent);
        color: var(--greeble-color-background);
        border: none;
        border-radius: var(--greeble-radius-medium, 8px);
        cursor: pointer;
        font-weight: 500;
        font-size: 0.875rem;
        transition: opacity 0.15s;
    }

    .export-btn:hover {
        opacity: 0.9;
    }

    .export-btn--secondary {
        background: rgba(255, 255, 255, 0.08);
        color: var(--greeble-color-foreground);
    }

    .export-btn__icon {
        font-size: 0.9rem;
    }

    /* Main Preview Area */
    .playground-main {
        padding: 1.5rem;
        overflow-y: auto;
    }

    .preview-header {
        margin-bottom: 1.5rem;
    }

    .preview-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
    }

    .preview-subtitle {
        font-size: 0.85rem;
        color: var(--greeble-color-muted);
        margin: 0;
    }

    /* Preview Grid */
    .preview-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.2rem;
        margin-bottom: 1.5rem;
    }

    .preview-block {
        position: relative;
    }

    .preview-block--wide {
        grid-column: 1 / -1;
    }

    .preview-block__label {
        position: absolute;
        top: -0.5rem;
        left: 0.75rem;
        background: var(--greeble-color-background);
        padding: 0 0.35rem;
        font-size: 0.65rem;
        color: var(--greeble-color-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Card Styles */
    .greeble-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--greeble-radius-medium, 12px);
        padding: 1rem;
        box-shadow: var(--greeble-shadow-2);
    }

    .preview-card__header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.5rem;
    }

    .preview-card__description {
        color: var(--greeble-color-muted);
        font-size: 0.8rem;
        margin: 0 0 1rem 0;
    }

    .preview-card__stats {
        display: flex;
        gap: 1.2rem;
    }

    .preview-stat {
        display: flex;
        flex-direction: column;
    }

    .preview-stat__value {
        font-size: 1.2rem;
        font-weight: 700;
    }

    .preview-stat__label {
        font-size: 0.65rem;
        color: var(--greeble-color-muted);
    }

    /* Form Styles */
    .preview-form__description {
        color: var(--greeble-color-muted);
        font-size: 0.8rem;
        margin: 0 0 1rem 0;
    }

    .preview-form__fields {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
    }

    .form-label {
        font-size: 0.75rem;
        font-weight: 500;
    }

    .form-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .greeble-select,
    .greeble-textarea {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--greeble-radius-medium, 8px);
        padding: 0.4rem 0.6rem;
        color: var(--greeble-color-foreground);
        font-family: inherit;
        font-size: 0.8rem;
    }

    .greeble-textarea {
        resize: vertical;
        min-height: 60px;
    }

    /* Button Styles */
    .preview-buttons__title {
        font-size: 0.7rem;
        font-weight: 500;
        color: var(--greeble-color-muted);
        margin: 0 0 0.5rem 0;
    }

    .preview-buttons__title:not(:first-child) {
        margin-top: 0.75rem;
    }

    .button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
    }

    .greeble-button--secondary {
        background: rgba(255, 255, 255, 0.08);
        color: var(--greeble-color-foreground);
        border-color: rgba(255, 255, 255, 0.12);
    }

    .greeble-button--ghost {
        background: transparent;
        border-color: transparent;
    }

    .greeble-button--ghost:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .greeble-button--destructive {
        background: #ef4444;
        color: white;
        border-color: #ef4444;
    }

    .greeble-button--sm {
        padding: 0.3rem 0.6rem;
        font-size: 0.8rem;
    }

    .greeble-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .greeble-button--loading {
        position: relative;
    }

    .spinner {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 2px solid currentColor;
        border-right-color: transparent;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Toast Styles */
    .preview-toasts {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .greeble-toast {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.6rem 0.75rem;
        background: rgba(255, 255, 255, 0.08);
        border-radius: var(--greeble-radius-medium, 8px);
        border-left: 3px solid var(--greeble-color-accent);
    }

    .greeble-toast--success {
        border-left-color: #22c55e;
    }

    .greeble-toast--info {
        border-left-color: var(--greeble-color-accent);
    }

    .greeble-toast--warning {
        border-left-color: #eab308;
    }

    .greeble-toast__icon {
        font-size: 0.85rem;
        line-height: 1;
    }

    .greeble-toast__content {
        flex: 1;
    }

    .greeble-toast__title {
        display: block;
        font-weight: 500;
        font-size: 0.8rem;
        margin-bottom: 0.15rem;
    }

    .greeble-toast__message {
        font-size: 0.7rem;
        color: var(--greeble-color-muted);
        margin: 0;
    }

    /* Table Styles */
    .preview-table-wrap {
        overflow: hidden;
    }

    .preview-table-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    .greeble-input--search {
        width: 160px;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.3rem 0.6rem;
        font-size: 0.8rem;
    }

    .greeble-table {
        width: 100%;
        border-collapse: collapse;
    }

    .greeble-table th,
    .greeble-table td {
        padding: 0.5rem;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        font-size: 0.8rem;
    }

    .greeble-table th {
        font-size: 0.65rem;
        font-weight: 500;
        color: var(--greeble-color-muted);
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .greeble-table code {
        background: rgba(255, 255, 255, 0.06);
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }

    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 500;
    }

    .status-badge--success {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
    }

    .status-badge--warning {
        background: rgba(234, 179, 8, 0.15);
        color: #eab308;
    }

    /* Tabs Styles */
    .greeble-tabs__list {
        display: flex;
        gap: 0.2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 0.75rem;
    }

    .greeble-tabs__tab {
        padding: 0.4rem 0.75rem;
        background: none;
        border: none;
        color: var(--greeble-color-muted);
        cursor: pointer;
        font-size: 0.75rem;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
        transition: color 0.15s, border-color 0.15s;
    }

    .greeble-tabs__tab:hover {
        color: var(--greeble-color-foreground);
    }

    .greeble-tabs__tab[data-active="true"] {
        color: var(--greeble-color-accent);
        border-bottom-color: var(--greeble-color-accent);
    }

    .greeble-tabs__panel {
        font-size: 0.8rem;
        color: var(--greeble-color-muted);
    }

    /* Input Styles */
    .preview-inputs {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .input-with-icon {
        position: relative;
    }

    .input-icon {
        position: absolute;
        left: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.9rem;
    }

    .input-with-icon .greeble-input {
        padding-left: 2.25rem;
    }

    .greeble-input--error {
        border-color: #ef4444;
    }

    .input-error-text {
        font-size: 0.8rem;
        color: #ef4444;
    }

    /* Modal Styles */
    .preview-modal-wrap p {
        color: var(--greeble-color-muted);
        margin: 0 0 1rem 0;
    }

    .modal-preview {
        position: fixed;
        inset: 0;
        z-index: 1000;
        display: grid;
        place-items: center;
    }

    .modal-preview[hidden] {
        display: none;
    }

    .modal-preview .greeble-modal__backdrop {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
    }

    .modal-preview .greeble-modal__panel {
        position: relative;
        max-width: 400px;
        width: 90%;
    }

    .modal-preview__header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .modal-preview__header .greeble-icon-button {
        font-size: 1.5rem;
        padding: 0.25rem;
    }

    .modal-preview p {
        color: var(--greeble-color-muted);
        margin: 0 0 1.25rem 0;
    }

    .modal-preview__actions {
        display: flex;
        gap: 0.5rem;
        justify-content: flex-end;
    }

    /* Code Output */
    .code-output {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--greeble-radius-medium, 12px);
        overflow: hidden;
    }

    .code-output__header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .code-output__title {
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0;
    }

    .code-output__code {
        margin: 0;
        padding: 1rem;
        overflow-x: auto;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.8rem;
        line-height: 1.6;
        color: var(--greeble-color-muted);
    }

    .code-output__code code {
        display: block;
        white-space: pre;
    }

    /* Copy Toast */
    .copy-toast {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        background: var(--greeble-color-accent);
        color: var(--greeble-color-background);
        padding: 0.6rem 1.25rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        opacity: 0;
        transition: opacity 0.3s, transform 0.3s;
        z-index: 9999;
    }

    .copy-toast.show {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }
    </style>
    """


@app.get("/", response_class=HTMLResponse)
async def playground() -> HTMLResponse:
    """Render the theme playground."""
    template_path = SITE_TEMPLATES / "playground.html"
    template = Template(template_path.read_text(encoding="utf-8"))
    html = template.substitute(
        styles=build_styles(),
        sidebar=build_sidebar_html(),
        preview=build_preview_blocks_html(),
        customizer=build_customizer_html(),
        javascript=build_javascript(),
    )
    return HTMLResponse(html)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.site.playground:app", host=str(HOST), port=int(PORT), reload=True)
