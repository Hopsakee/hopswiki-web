"""Search page: filter wiki pages by title, content, tags."""

from nicegui import ui

from app.components.badges import type_badge
from app.components.layout import page_layout
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

            def do_search(e) -> None:
                query = e.value.strip()
                results_container.clear()
                if not query or len(query) < 2:
                    return
                results = store.search(query)
                with results_container:
                    if not results:
                        ui.label("No results found.").style("color: var(--text-muted)")
                        return
                    ui.label(f"{len(results)} results").style(
                        "color: var(--text-muted); font-size: 0.875rem"
                    )
                    for page in results:
                        with ui.link(target=page.url).classes("no-underline w-full"):
                            with ui.element("div").classes(
                                "wiki-card flex items-center gap-4"
                            ):
                                type_badge(page.type)
                                with ui.column().classes("flex-1 gap-1"):
                                    ui.label(page.title).style(
                                        "color: var(--text-primary); font-size: 0.875rem; font-weight: 500"
                                    )
                                    ui.label(page.snippet[:150]).style(
                                        "color: var(--text-muted); font-size: 0.75rem"
                                    )

            ui.input(
                placeholder="Search by title, content, or tags...",
                on_change=do_search,
            ).classes("w-full search-input").props('clearable outlined debounce="300"')
