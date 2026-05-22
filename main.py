import hmac
import logging
import threading
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

    reload_min_interval_s = settings.reload_min_interval_s
    throttle_lock = threading.Lock()
    last_reload_at = 0.0

    @app.post("/_reload")
    def reload_endpoint(request: Request) -> dict:
        nonlocal last_reload_at
        client = request.client.host if request.client else "unknown"
        if not reload_token:
            logger.warning("/_reload denied from %s — RELOAD_TOKEN not configured", client)
            raise HTTPException(status_code=503, detail="reload disabled: RELOAD_TOKEN unset")
        header_token = (request.headers.get("X-Reload-Token") or "").strip()
        if not hmac.compare_digest(header_token, reload_token):
            logger.warning("/_reload denied from %s — bad or missing X-Reload-Token", client)
            raise HTTPException(status_code=401, detail="unauthorized")
        # Throttle: refuse if a reload was accepted less than reload_min_interval_s
        # ago. Lock makes check+set atomic so concurrent valid-token callers
        # serialize — one wins and proceeds to load(), the rest get 429.
        # Counts on accept (not on success) — a failed load still counts as
        # "you triggered a load attempt, wait before triggering another".
        with throttle_lock:
            now = time.monotonic()
            elapsed = now - last_reload_at
            if reload_min_interval_s > 0 and elapsed < reload_min_interval_s:
                retry_after = reload_min_interval_s - elapsed
                logger.warning(
                    "/_reload throttled from %s — %.1fs since last accepted reload (min %.0fs)",
                    client, elapsed, reload_min_interval_s,
                )
                raise HTTPException(
                    status_code=429,
                    detail=f"reload throttled: retry in {retry_after:.0f}s",
                    headers={"Retry-After": str(max(1, int(retry_after) + 1))},
                )
            last_reload_at = now
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
        # WikiStore.load() does NOT raise when wiki_path is missing or unreadable —
        # it silently produces zero pages. Reject the swap in that case so a
        # misconfigured mount or temporarily-missing wiki dir cannot nuke the live
        # store. A legitimately empty wiki (old_count == 0) is allowed through.
        if len(new_store.pages) == 0 and old_count > 0:
            logger.error(
                "/_reload refused from %s — rebuilt store is empty (%d -> 0), keeping previous state",
                client, old_count,
            )
            raise HTTPException(
                status_code=500,
                detail="reload refused: rebuilt store is empty",
            )
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
