"""Shared sortable/filterable page list with collapsible tag filter."""

from __future__ import annotations

from html import escape

from nicegui import ui

from app.components.badges import type_badge
from app.wiki import WikiPage, WikiStore

SORT_OPTIONS = {
    "name": "Name",
    "backlinks": "In-links",
    "outlinks": "Out-links",
    "total_links": "Total links",
}

SORT_KEYS = {
    "name": lambda p: p._title_lower,
    "backlinks": lambda p: (-len(p.backlinks), p._title_lower),
    "outlinks": lambda p: (-len(p.outlinks), p._title_lower),
    "total_links": lambda p: (-(len(p.backlinks) + len(p.outlinks)), p._title_lower),
}


def _collect_tags(pages: list[WikiPage]) -> list[str]:
    tags: set[str] = set()
    for p in pages:
        tags.update(p.tags)
    return sorted(tags)


def tag_pill(tag: str, active: bool = False, on_click=None) -> None:
    """Render a tag pill. Shared across all pages for consistent styling."""
    cls = "tag-pill tag-pill-active" if active else "tag-pill"
    el = ui.html(f'<span class="{cls}">{escape(tag)}</span>')
    if on_click:
        el.on("click", on_click).style("cursor: pointer")


def page_list_controls(
    pages: list[WikiPage],
    store: WikiStore,
    *,
    show_type_badge: bool = True,
) -> None:
    state = {"sort": "name", "active_tags": set(), "tags_expanded": False}
    available_tags = _collect_tags(pages)

    def toggle_tag(tag: str) -> None:
        if tag in state["active_tags"]:
            state["active_tags"].discard(tag)
        else:
            state["active_tags"].add(tag)
        render_filter_bar()
        render_list()

    def clear_tags() -> None:
        state["active_tags"].clear()
        render_filter_bar()
        render_list()

    def toggle_tags_panel() -> None:
        state["tags_expanded"] = not state["tags_expanded"]
        render_filter_bar()

    def on_sort_change(e) -> None:
        state["sort"] = e.value
        render_list()

    # === Controls bar: sort + filter button + active filter display ===
    with ui.row().classes("w-full items-center gap-3 flex-wrap"):
        ui.select(
            options=SORT_OPTIONS,
            value="name",
            label="Sort by",
            on_change=on_sort_change,
        ).classes("w-40 sort-select").props("outlined dense")

        filter_bar = ui.element("div").classes("flex-1")

    # === Collapsible tag cloud (hidden by default) ===
    tag_panel = ui.element("div")

    # === Page list ===
    list_container = ui.column().classes("w-full gap-1")

    def render_filter_bar() -> None:
        filter_bar.clear()
        tag_panel.clear()

        with filter_bar:
            with ui.row().classes("items-center gap-2 flex-wrap"):
                if state["active_tags"]:
                    # Show active filters
                    ui.label("Filtered on:").style(
                        "color: var(--text-muted); font-size: 0.8rem"
                    )
                    for tag in sorted(state["active_tags"]):
                        tag_pill(tag, True, lambda t=tag: toggle_tag(t))
                    ui.button(
                        "Clear filter", on_click=clear_tags
                    ).props("flat dense size=xs").style("color: var(--text-muted)")

                btn_label = "Hide tags" if state["tags_expanded"] else "Filter by tags"
                btn_icon = "expand_less" if state["tags_expanded"] else "filter_list"
                ui.button(
                    btn_label, icon=btn_icon, on_click=toggle_tags_panel
                ).props("flat dense size=sm").style(
                    "color: var(--accent); font-size: 0.8rem"
                )

        if state["tags_expanded"]:
            with tag_panel:
                with ui.element("div").classes("filter-panel").style("padding: 0.75rem"):
                    with ui.row().classes("flex-wrap gap-1"):
                        for tag in available_tags:
                            is_active = tag in state["active_tags"]
                            tag_pill(tag, is_active, lambda t=tag: toggle_tag(t))

    def render_list() -> None:
        list_container.clear()
        filtered = pages
        if state["active_tags"]:
            filtered = [
                p for p in filtered
                if state["active_tags"].issubset(set(p.tags))
            ]

        key_fn = SORT_KEYS.get(state["sort"], SORT_KEYS["name"])
        sorted_pages = sorted(filtered, key=key_fn)

        with list_container:
            ui.label(f"{len(sorted_pages)} pages").style(
                "color: var(--text-muted); font-size: 0.8rem"
            )
            for page in sorted_pages:
                with ui.row().classes(
                    "w-full items-center gap-3 px-4 py-2 rounded-lg"
                ).style("transition: background-color 0.15s"):
                    if show_type_badge:
                        type_badge(page.type)
                    ui.link(page.title, page.url).classes("no-underline").style(
                        "color: var(--text-primary); font-size: 0.875rem; flex: 1"
                    )
                    if page.tags:
                        with ui.row().classes("gap-1 flex-wrap"):
                            for tag in page.tags[:4]:
                                is_active = tag in state["active_tags"]
                                tag_pill(
                                    tag, is_active, lambda t=tag: toggle_tag(t)
                                )
                    ui.label(
                        f"{len(page.backlinks)}in {len(page.outlinks)}out"
                    ).style(
                        "color: var(--text-muted); font-size: 0.7rem; white-space: nowrap"
                    )

    # Initial render
    render_filter_bar()
    render_list()
