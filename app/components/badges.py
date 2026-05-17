"""Type badge component for wiki page types."""

from nicegui import ui

from app.wiki import TYPE_CONFIG


def type_badge(wiki_type: str) -> None:
    """Render a type badge. CSS is in layout.py's APP_CSS."""
    cfg = TYPE_CONFIG.get(wiki_type, {"icon": "?"})
    ui.html(
        f'<span class="type-badge type-badge-{wiki_type}">'
        f'{cfg["icon"]} {wiki_type}</span>'
    )
