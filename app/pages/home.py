"""Home page: folder cards + sortable/filterable page list."""

from nicegui import ui

from app.components.layout import page_layout
from app.components.page_list import page_list_controls
from app.config import Settings
from app.wiki import FOLDER_TO_TYPE, TYPE_CONFIG, WIKI_FOLDERS, WikiStore


def register(store: WikiStore, settings: Settings) -> None:

    @ui.page("/")
    def home_page() -> None:
        with page_layout("Home"):
            stats = store.get_stats()

            ui.html(
                "<span style=\"font-family: var(--serif); font-size: 2.25rem; "
                "font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em;\">"
                "A personal wiki across three domains."
                "</span>"
            )
            ui.label(
                f"{stats.total_pages} pages \u00b7 {stats.total_links} cross-references"
            ).style(
                "color: var(--text-muted); font-size: 0.75rem; letter-spacing: 0.14em; "
                "text-transform: uppercase; margin-top: -0.25rem"
            )

            # Folder cards
            with ui.row().classes("w-full gap-4 flex-wrap"):
                for folder in WIKI_FOLDERS:
                    wiki_type = FOLDER_TO_TYPE[folder]
                    cfg = TYPE_CONFIG.get(wiki_type, {})
                    count = stats.counts.get(folder, 0)
                    with ui.link(target=f"/wiki/{folder}").classes("no-underline flex-1 min-w-[180px]"):
                        with ui.element("div").classes("wiki-card cursor-pointer"):
                            ui.label(f"{cfg.get('icon', '')} {folder.title()}").style(
                                "color: var(--card-text); font-size: 1rem; font-weight: 600"
                            )
                            ui.label(f"{count} pages").style(
                                "color: var(--card-text-muted); font-size: 0.875rem; margin-top: 0.25rem"
                            )

            # All pages with sort + filter
            ui.html(
                "<span style=\"font-family: var(--serif); font-size: 1.4rem; "
                "font-weight: 700; color: var(--text-primary); display: block; "
                "margin-top: 1.2rem;\">All Pages</span>"
            )
            page_list_controls(store.get_all_pages(), store)
