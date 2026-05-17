"""Folder view: sortable/filterable list of pages in a wiki category."""

from nicegui import ui

from app.components.layout import page_layout
from app.components.page_list import page_list_controls
from app.config import Settings
from app.wiki import FOLDER_TO_TYPE, TYPE_CONFIG, WIKI_FOLDERS, WikiStore


def register(store: WikiStore, settings: Settings) -> None:

    @ui.page("/wiki/{folder}")
    def folder_page(folder: str) -> None:
        if folder not in WIKI_FOLDERS:
            with page_layout("Not Found"):
                ui.label(f"Unknown folder: {folder}").style("color: var(--error)")
            return

        pages = store.get_folder_pages(folder)
        wiki_type = FOLDER_TO_TYPE[folder]
        cfg = TYPE_CONFIG.get(wiki_type, {})

        with page_layout(folder.title()):
            with ui.row().classes("items-center gap-3"):
                ui.label(f"{cfg.get('icon', '')} {folder.title()}").style(
                    "color: var(--text-primary); font-size: 1.5rem; font-weight: 700"
                )
                ui.label(f"{len(pages)} pages").style(
                    "color: var(--text-muted); font-size: 0.875rem"
                )

            page_list_controls(pages, store, show_type_badge=False)
