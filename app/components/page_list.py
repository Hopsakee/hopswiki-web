"""Shared sortable/filterable page list with collapsible tag filter."""

from __future__ import annotations

from html import escape

from nicegui import ui

from app.components.badges import type_badge
from app.components.pagination import paginate, pagination_controls
from app.wiki import WikiPage, WikiStore

SORT_OPTIONS = {
    "name": "Name",
    "backlinks": "In-links",
    "outlinks": "Out-links",
    "total_links": "Total links",
}

# Every key ends in `p.slug` so the order is total: two pages can share a title
# (one pair does today), and a tie that resolves differently between two renders
# would let an item jump across a window boundary — appearing twice, or not at all.
SORT_KEYS = {
    "name": lambda p: (p._title_lower, p.slug),
    "backlinks": lambda p: (-len(p.backlinks), p._title_lower, p.slug),
    "outlinks": lambda p: (-len(p.outlinks), p._title_lower, p.slug),
    "total_links": lambda p: (
        -(len(p.backlinks) + len(p.outlinks)), p._title_lower, p.slug
    ),
}


def _collect_tags(pages: list[WikiPage]) -> list[str]:
    tags: set[str] = set()
    for p in pages:
        tags.update(p.tags)
    return sorted(tags)


def _pill_html(tag: str, active: bool) -> str:
    cls = "tag-pill tag-pill-active" if active else "tag-pill"
    return f'<span class="{cls}">{escape(tag)}</span>'


def tag_pill(tag: str, active: bool = False, on_click=None) -> ui.html:
    """Render a tag pill. Shared across all pages for consistent styling.

    Returns the element so a caller can restyle it in place via `set_content`
    instead of rebuilding its container.
    """
    el = ui.html(_pill_html(tag, active))
    if on_click:
        el.on("click", on_click).style("cursor: pointer")
    return el


def page_list_controls(
    pages: list[WikiPage],
    store: WikiStore,
    *,
    show_type_badge: bool = True,
) -> None:
    state = {"sort": "name", "active_tags": set(), "tags_expanded": False, "page": 0}
    available_tags = _collect_tags(pages)
    # Panel pills are held by tag so a toggle can restyle the one that changed.
    # Rebuilding the panel instead would construct one element per distinct tag
    # (2498 of them at the current dataset size) on every single tag click.
    panel_pills: dict[str, ui.html] = {}

    def sync_panel_pill(tag: str) -> None:
        el = panel_pills.get(tag)
        if el is not None:
            el.set_content(_pill_html(tag, tag in state["active_tags"]))

    def after_filter_change() -> None:
        # A changed filter always returns to the first window: keeping the user
        # on page 12 of a list that just shrank to 3 pages is worse than resetting.
        state["page"] = 0
        render_active_row()
        render_list()

    def toggle_tag(tag: str) -> None:
        if tag in state["active_tags"]:
            state["active_tags"].discard(tag)
        else:
            state["active_tags"].add(tag)
        sync_panel_pill(tag)
        after_filter_change()

    def clear_tags() -> None:
        cleared = list(state["active_tags"])
        state["active_tags"].clear()
        for tag in cleared:
            sync_panel_pill(tag)
        after_filter_change()

    def toggle_tags_panel() -> None:
        state["tags_expanded"] = not state["tags_expanded"]
        render_active_row()
        render_tag_panel()

    def on_sort_change(e) -> None:
        state["sort"] = e.value
        state["page"] = 0
        render_list()

    def go_to_page(page: int) -> None:
        state["page"] = page
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

    def render_active_row() -> None:
        filter_bar.clear()

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

    def render_tag_panel() -> None:
        tag_panel.clear()
        panel_pills.clear()
        if not state["tags_expanded"]:
            return
        with tag_panel:
            with ui.element("div").classes("filter-panel").style("padding: 0.75rem"):
                with ui.row().classes("flex-wrap gap-1"):
                    for tag in available_tags:
                        panel_pills[tag] = tag_pill(
                            tag,
                            tag in state["active_tags"],
                            lambda t=tag: toggle_tag(t),
                        )

    def render_list() -> None:
        list_container.clear()
        filtered = pages
        if state["active_tags"]:
            filtered = [
                p for p in filtered
                if state["active_tags"].issubset(set(p.tags))
            ]

        key_fn = SORT_KEYS.get(state["sort"], SORT_KEYS["name"])
        # Sort and filter run over the FULL dataset; only the window is rendered,
        # so ordering and counts stay globally correct at any page size.
        window = paginate(sorted(filtered, key=key_fn), state["page"])
        state["page"] = window.index

        with list_container:
            ui.label(window.summary("pages")).style(
                "color: var(--text-muted); font-size: 0.8rem"
            )
            for page in window.items:
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

            pagination_controls(window, go_to_page)

    # Initial render
    render_active_row()
    render_list()
