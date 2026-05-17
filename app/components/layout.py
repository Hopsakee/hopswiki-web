"""Shared layout: header, navigation, page wrapper.

Theme follows PAI/USER/UIDESIGNSTYLE.md: warm dark palette, serif headings,
sharp 0-2px corners, flat surfaces (no shadows, no gradients), low contrast,
formal register. Personal-palette accents only (no WDODelta brand).
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from nicegui import app, ui

APP_CSS = """
:root, body.body--dark {
    --bg-primary: #0e0c0a;
    --bg-secondary: #15110d;
    --bg-card: #1a1612;
    --card-text: #f0e8dc;
    --card-text-muted: #8a807a;
    --text-primary: #f0e8dc;
    --text-secondary: #c8bdac;
    --text-muted: #8a807a;
    --accent: #f46a25;
    --accent-hover: #28a197;
    --accent-soft: #2a1c10;
    --border: #2a241e;
    --hover-bg: rgba(244, 106, 37, 0.08);
    --header-bg: #0a0806;
    --badge-bg: rgba(244, 106, 37, 0.10);
    --badge-text: #f0d4b8;
    --badge-border: rgba(244, 106, 37, 0.22);
    --tag-bg: #1a1612;
    --tag-text: #c8bdac;
    --tag-border: #2a241e;
    --tag-active-bg: #801650;
    --tag-active-text: #f0e8dc;
    --error: #b91c1c;
    --serif: Georgia, "Instrument Serif", "Playfair Display", "Source Serif Pro", serif;
    --sans: -apple-system, BlinkMacSystemFont, "Inter", "Helvetica Neue", Arial, sans-serif;
}

body.body--light {
    --bg-primary: #faf6ef;
    --bg-secondary: #f2ece0;
    --bg-card: #ffffff;
    --card-text: #2a241e;
    --card-text-muted: #6a5f53;
    --text-primary: #2a241e;
    --text-secondary: #4a4036;
    --text-muted: #6a5f53;
    --accent: #801650;
    --accent-hover: #f46a25;
    --accent-soft: #f6e9e3;
    --border: rgba(42, 36, 30, 0.18);
    --hover-bg: rgba(128, 22, 80, 0.06);
    --header-bg: #faf6ef;
    --badge-bg: rgba(128, 22, 80, 0.06);
    --badge-text: #801650;
    --badge-border: rgba(128, 22, 80, 0.18);
    --tag-bg: #f2ece0;
    --tag-text: #4a4036;
    --tag-border: rgba(42, 36, 30, 0.20);
    --tag-active-bg: #801650;
    --tag-active-text: #faf6ef;
    --error: #b91c1c;
}

body {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--sans);
    letter-spacing: 0.005em;
}

.q-page { background-color: var(--bg-primary) !important; }
.q-layout { background-color: var(--bg-primary) !important; }

/* Cards — flat, sharp, low contrast */
.wiki-card {
    background-color: var(--bg-card);
    color: var(--card-text);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.1rem 1.25rem;
    transition: border-color 0.15s;
    box-shadow: none;
}
.wiki-card:hover {
    border-color: var(--accent);
}

.filter-panel {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 2px;
}

/* Wiki content typography — serif headings, sans body */
.wiki-content h1 {
    font-family: var(--serif);
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin: 1.75rem 0 0.75rem;
    color: var(--text-primary);
}
.wiki-content h2 {
    font-family: var(--serif);
    font-size: 1.5rem;
    font-weight: 700;
    margin: 1.4rem 0 0.6rem;
    color: var(--accent);
}
.wiki-content h3 {
    font-family: var(--serif);
    font-size: 1.2rem;
    font-weight: 700;
    margin: 1.1rem 0 0.5rem;
    color: var(--accent);
}
.wiki-content p {
    margin: 0.6rem 0;
    line-height: 1.75;
    color: var(--text-secondary);
}

/* Lists — explicit bullet/number styles */
.wiki-content ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
    color: var(--text-secondary);
    list-style-type: disc;
}
.wiki-content ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
    color: var(--text-secondary);
    list-style-type: decimal;
}
.wiki-content ul ul { list-style-type: circle; }
.wiki-content ul ul ul { list-style-type: square; }
.wiki-content li {
    margin: 0.25rem 0;
    line-height: 1.7;
    display: list-item;
}

.wiki-content blockquote {
    border-left: 2px solid var(--accent);
    padding: 0.5rem 1rem;
    margin: 0.75rem 0;
    color: var(--text-secondary);
    background-color: var(--accent-soft);
    border-radius: 0;
    font-style: italic;
}
.wiki-content code {
    background-color: var(--bg-secondary);
    padding: 0.15rem 0.4rem;
    border-radius: 2px;
    font-size: 0.875em;
    color: var(--accent);
    font-family: "JetBrains Mono", "Source Code Pro", Consolas, monospace;
}
.wiki-content pre {
    background-color: var(--bg-secondary);
    padding: 1rem;
    border-radius: 2px;
    overflow-x: auto;
    border: 1px solid var(--border);
}
.wiki-content pre code { background: none; padding: 0; color: var(--text-secondary); }
.wiki-content table { border-collapse: collapse; width: 100%; margin: 0.75rem 0; }
.wiki-content th, .wiki-content td {
    border: 1px solid var(--border);
    padding: 0.5rem 0.75rem;
    text-align: left;
}
.wiki-content th { background-color: var(--bg-secondary); font-weight: 600; }
.wiki-content hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

.wiki-content a.wikilink {
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px solid var(--border);
    transition: border-color 0.15s, color 0.15s;
}
.wiki-content a.wikilink:hover {
    color: var(--accent-hover);
    border-bottom-color: var(--accent-hover);
}
.wiki-content .wikilink-broken {
    color: var(--text-muted);
    text-decoration: line-through;
    cursor: not-allowed;
}
.wiki-content a { color: var(--accent); text-decoration: none; }
.wiki-content a:hover { color: var(--accent-hover); text-decoration: underline; }

.sidebar-link {
    color: var(--card-text) !important;
    cursor: pointer;
    font-size: 0.875rem;
    transition: color 0.15s;
}
.sidebar-link:hover { color: var(--accent); }

.search-input .q-field__control {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--text-primary) !important;
    box-shadow: none !important;
}

/* Tag pills — sharp, low-contrast */
.tag-pill {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.15s;
    background-color: var(--tag-bg);
    color: var(--tag-text);
    border: 1px solid var(--tag-border);
    letter-spacing: 0.02em;
}
.tag-pill:hover {
    border-color: var(--accent);
    color: var(--accent);
}
.tag-pill-active {
    background-color: var(--tag-active-bg) !important;
    color: var(--tag-active-text) !important;
    border-color: var(--tag-active-bg) !important;
}

/* Sort select styling */
.sort-select .q-field__control {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--text-primary) !important;
    min-height: 36px !important;
    box-shadow: none !important;
}
.sort-select .q-field__label { color: var(--text-muted) !important; }
.sort-select .q-field__native,
.sort-select .q-field__input { color: var(--text-primary) !important; }

/* Header — flat, no shadow */
.hopswiki-header {
    background-color: var(--header-bg) !important;
    border-bottom: 1px solid var(--border) !important;
    box-shadow: none !important;
}
.hopswiki-wordmark {
    font-family: var(--serif);
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    color: var(--text-primary);
    line-height: 1;
}
.hopswiki-wordmark-accent { color: var(--accent); }
.hopswiki-tagline {
    font-family: var(--sans);
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 0.15rem;
}

/* Help pill — visually separated from function-page links */
.header-help-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.25rem 0.65rem;
    margin-left: 0.5rem;
    border-radius: 2px;
    border: 1px solid var(--border);
    color: var(--text-muted) !important;
    background-color: transparent;
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: border-color 0.15s, color 0.15s, background-color 0.15s;
}
.header-help-pill:hover {
    color: var(--accent-hover) !important;
    border-color: var(--accent-hover);
    background-color: var(--accent-soft);
}

/* Type badges — personal palette */
.type-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: lowercase;
    white-space: nowrap;
    background-color: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border);
}

body.body--dark .type-badge-entity     { background-color: #0d2a27; color: #8ed2ca; border-color: #28a197; }
body.body--light .type-badge-entity    { background-color: #e3f3f0; color: #14635c; border-color: #28a197; }

body.body--dark .type-badge-concept    { background-color: #3a1a08; color: #f9b487; border-color: #f46a25; }
body.body--light .type-badge-concept   { background-color: #fdeadc; color: #b04a10; border-color: #f46a25; }

body.body--dark .type-badge-source     { background-color: #211a33; color: #c7b0e8; border-color: #a285d1; }
body.body--light .type-badge-source    { background-color: #ece4f6; color: #5a3f8c; border-color: #a285d1; }

body.body--dark .type-badge-comparison { background-color: #2d0b1d; color: #d49ab9; border-color: #801650; }
body.body--light .type-badge-comparison{ background-color: #f4dde9; color: #801650; border-color: #801650; }

body.body--dark .type-badge-synthesis  { background-color: #0a2c3d; color: #9cd5ee; border-color: #6bbce6; }
body.body--light .type-badge-synthesis { background-color: #def0fa; color: #2073bc; border-color: #6bbce6; }
"""


def add_head_html() -> None:
    ui.add_head_html(f"<style>{APP_CSS}</style>")


def header() -> None:
    with ui.header().classes("hopswiki-header"):
        with ui.row().classes("w-full items-center px-6 py-3"):
            with ui.link(target="/").classes("no-underline"):
                with ui.column().classes("gap-0"):
                    ui.html(
                        '<span class="hopswiki-wordmark">'
                        'Hops<span class="hopswiki-wordmark-accent">wiki</span>'
                        '</span>'
                    )
                    ui.html('<span class="hopswiki-tagline">personal reading room</span>')
            ui.space()
            for label, href in [
                ("Home", "/"),
                ("Search", "/search"),
            ]:
                ui.link(label, href).classes(
                    "no-underline text-sm font-medium"
                ).style("color: var(--accent)")
            for folder in ("entities", "concepts", "sources", "comparisons", "syntheses"):
                ui.link(
                    folder.title(), f"/wiki/{folder}"
                ).classes("no-underline text-sm").style("color: var(--text-secondary)")

            # Help pill — distinct from function pages (muted outline, icon-led)
            ui.link("? Help", "/help").classes(
                "no-underline text-xs header-help-pill"
            )

            # Dark mode toggle — persisted via app.storage.user
            is_dark = app.storage.user.get("dark_mode", True)
            dark = ui.dark_mode(value=is_dark)

            dark_btn = ui.button(
                icon="light_mode" if is_dark else "dark_mode",
            ).props("flat round size=sm").style("color: var(--text-secondary)")

            def toggle_dark() -> None:
                dark.toggle()
                app.storage.user["dark_mode"] = dark.value
                dark_btn.props(f'icon={"light_mode" if dark.value else "dark_mode"}')

            dark_btn.on("click", toggle_dark)


@contextmanager
def page_layout(title: str = "") -> Generator[None, None, None]:
    add_head_html()
    if title:
        ui.page_title(f"{title} — Hopswiki")
    header()
    with ui.column().classes("w-full max-w-6xl mx-auto px-6 py-8 gap-6"):
        yield
