from dataclasses import dataclass
from pathlib import Path
import logging
import os

from dotenv import load_dotenv

_logger = logging.getLogger(__name__)


def env_flag(key: str, default: bool = False) -> bool:
    val = os.getenv(key, "").lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "on")


def read_secret(name: str) -> str:
    # Authelia-style _FILE convention: prefer ${NAME}_FILE pointing to a path
    # whose contents are the secret; fall back to ${NAME} for local dev.
    # Failing to read the file returns "" (fail-closed — handler returns 503).
    file_path = os.getenv(f"{name}_FILE", "").strip()
    if file_path:
        try:
            return Path(file_path).read_text(encoding="utf-8").strip()
        except OSError as exc:
            _logger.error("%s_FILE set to %s but unreadable: %s", name, file_path, exc)
            return ""
    return os.getenv(name, "").strip()


@dataclass(slots=True)
class Settings:
    wiki_path: Path
    title: str
    host: str
    port: int
    dark_mode: bool
    storage_secret: str
    reload_token: str
    reload_min_interval_s: float

    @property
    def wiki_exists(self) -> bool:
        return self.wiki_path.is_dir()


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        wiki_path=Path(os.getenv("WIKI_PATH", "~/Drive/Hopswiki/wiki")).expanduser(),
        title=os.getenv("APP_TITLE", "Hopswiki"),
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8082")),
        dark_mode=env_flag("DARK_MODE", default=True),
        storage_secret=os.getenv("STORAGE_SECRET", "hopswiki-web-storage-secret"),
        reload_token=read_secret("RELOAD_TOKEN"),
        reload_min_interval_s=max(0.0, float(os.getenv("RELOAD_MIN_INTERVAL_S", "30"))),
    )
