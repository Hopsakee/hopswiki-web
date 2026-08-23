"""Search page: filter wiki pages by title, content, tags."""

from nicegui import ui

from app.components.badges import type_badge
from app.components.layout import page_layout
from app.components.pagination import paginate, pagination_controls
from app.config import Settings
from app.wiki import WikiStore


def register(store: WikiStore, settings: Settings) -> None:

    @ui.page("/search")
    def search_page() -> None:
        with page_layout("Search"):
            ui.html(
                "<span style=\"font-family: var(--serif); font-size: 1.75rem; "
                "font-weight: 700; color: var(--text-primary);\">Search Hopswiki</span>"
            )

            results_container = ui.column().classes("w-full gap-2")
            query = ""
            page = 0

            def on_input(e) -> None:
                # A new query always starts at the first window; paging within
                # one query keeps its position.
                nonlocal query, page
                # `clearable` hands back None when the x is clicked.
                query, page = (e.value or "").strip(), 0
                render_results()

            def go_to_page(new_page: int) -> None:
                nonlocal page
                page = new_page
                render_results()

            def render_results() -> None:
                nonlocal page
                results_container.clear()
                if len(query) < 2:
                    return
                results = store.search(query)
                with results_container:
                    if not results:
                        ui.label("No results found.").style("color: var(--text-muted)")
                        return
                    window = paginate(results, page)
                    page = window.index
                    ui.label(window.summary("results")).style(
                        "color: var(--text-muted); font-size: 0.875rem"
                    )
                    for result in window.items:
                        with ui.link(target=result.url).classes("no-underline w-full"):
                            with ui.element("div").classes(
                                "wiki-card flex items-center gap-4"
                            ):
                                type_badge(result.type)
                                with ui.column().classes("flex-1 gap-1"):
                                    ui.label(result.title).style(
                                        "color: var(--text-primary); font-size: 0.875rem; font-weight: 500"
                                    )
                                    ui.label(result.snippet[:150]).style(
                                        "color: var(--text-muted); font-size: 0.75rem"
                                    )
                    pagination_controls(window, go_to_page)

            ui.input(
                placeholder="Search by title, content, or tags...",
                on_change=on_input,
            ).classes("w-full search-input").props('clearable outlined debounce="300"')
