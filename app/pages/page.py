"""Individual wiki page view: markdown content + backlinks/outlinks."""

from nicegui import ui

from app.components.badges import type_badge
from app.components.layout import page_layout
from app.components.markdown import render_wiki_markdown
from app.components.page_list import tag_pill
from app.config import Settings
from app.wiki import WikiStore


def _sidebar_link(store: WikiStore, slug: str, show_broken: bool = False) -> None:
    resolved = store.resolve_slug(slug)
    if resolved:
        folder, _ = resolved
        linked = store.get_page(folder, slug)
        title = linked.title if linked else slug
        ui.link(title, f"/wiki/{folder}/{slug}").classes("sidebar-link block")
    elif show_broken:
        ui.label(slug.replace("-", " ").title()).style(
            "color: var(--text-muted); font-size: 0.875rem; text-decoration: line-through"
        )


def _sidebar_section(
    label: str, slugs: list[str], store: WikiStore, *, show_broken: bool = False
) -> None:
    if not slugs:
        return
    with ui.element("div").classes("wiki-card"):
        ui.label(f"{label} ({len(slugs)})").style(
            "color: var(--card-text-muted); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem"
        )
        for slug in slugs:
            _sidebar_link(store, slug, show_broken=show_broken)


def register(store: WikiStore, settings: Settings) -> None:

    @ui.page("/wiki/{folder}/{slug}")
    def wiki_page(folder: str, slug: str) -> None:
        page = store.get_page(folder, slug)

        if not page:
            with page_layout("Not Found"):
                ui.label(f"Page not found: {folder}/{slug}").style("color: var(--error)")
            return

        with page_layout(page.title):
            with ui.row().classes("items-center gap-3 flex-wrap"):
                type_badge(page.type)
                ui.label(page.title).style(
                    "color: var(--text-primary); font-size: 1.5rem; font-weight: 700"
                )

            with ui.row().classes("gap-4 flex-wrap -mt-2"):
                if page.created:
                    ui.label(f"Created: {page.created}").style(
                        "color: var(--text-muted); font-size: 0.75rem"
                    )
                if page.updated:
                    ui.label(f"Updated: {page.updated}").style(
                        "color: var(--text-muted); font-size: 0.75rem"
                    )
                if page.tags:
                    for tag in page.tags:
                        tag_pill(tag)

            with ui.row().classes("w-full gap-6 items-start"):
                with ui.column().classes("flex-1 min-w-0"):
                    html = render_wiki_markdown(page.content, store)
                    ui.html(html).classes("wiki-content")

                with ui.column().classes("w-64 shrink-0 gap-4"):
                    _sidebar_section("Backlinks", sorted(page.backlinks), store)
                    _sidebar_section(
                        "Outlinks", sorted(set(page.outlinks)), store, show_broken=True
                    )
                    _sidebar_section("Sources", page.sources, store, show_broken=True)
