import hmac
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from app.config import load_settings
from app.pages import folder, help, home, page, search
from app.wiki import WikiStore
from fastapi import HTTPException, Request
from nicegui import app, ui

DATA_DIR = Path(__file__).resolve().parent / "data"

logger = logging.getLogger(__name__)


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

    reload_token = settings.reload_token
    if reload_token and len(reload_token) < 16:
        logger.warning(
            "RELOAD_TOKEN is set but only %d chars; recommend ≥16 for adequate entropy",
            len(reload_token),
        )

    @app.post("/_reload")
    def reload_endpoint(request: Request) -> dict:
        client = request.client.host if request.client else "unknown"
        if not reload_token:
            logger.warning("/_reload denied from %s — RELOAD_TOKEN not configured", client)
            raise HTTPException(status_code=503, detail="reload disabled: RELOAD_TOKEN unset")
        header_token = (request.headers.get("X-Reload-Token") or "").strip()
        if not hmac.compare_digest(header_token, reload_token):
            logger.warning("/_reload denied from %s — bad or missing X-Reload-Token", client)
            raise HTTPException(status_code=401, detail="unauthorized")
        t0 = time.perf_counter()
        try:
            new_store = WikiStore(store.wiki_path)
            new_store.load()
        except Exception as exc:
            logger.exception("/_reload failed from %s — load() raised", client)
            raise HTTPException(
                status_code=500,
                detail=f"reload failed: {exc.__class__.__name__}",
            ) from exc
        old_count = len(store.pages)
        store.replace_state_from(new_store)
        dt_ms = (time.perf_counter() - t0) * 1000
        new_count = len(store.pages)
        logger.info(
            "/_reload ok from %s — pages %d->%d (%+d), %.0f ms",
            client, old_count, new_count, new_count - old_count, dt_ms,
        )
        return {
            "status": "ok",
            "pages": new_count,
            "delta": new_count - old_count,
            "elapsed_ms": round(dt_ms, 1),
            "loaded_at": datetime.now(timezone.utc).isoformat(),
        }

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
