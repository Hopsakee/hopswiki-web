from pathlib import Path

from app.config import load_settings
from app.pages import folder, help, home, page, search
from app.wiki import WikiStore
from nicegui import app, ui

DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> None:
    settings = load_settings()

    store = WikiStore(settings.wiki_path)
    store.load()

    app.add_static_files("/static/data", str(DATA_DIR))

    home.register(store, settings)
    folder.register(store, settings)
    page.register(store, settings)
    search.register(store, settings)
    help.register(store, settings)

    ui.run(
        title=settings.title,
        host=settings.host,
        port=settings.port,
        reload=False,
        show=False,
        dark=settings.dark_mode,
        storage_secret=settings.storage_secret,
    )


if __name__ == "__main__":
    main()
