from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


def env_flag(key: str, default: bool = False) -> bool:
    val = os.getenv(key, "").lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "on")


@dataclass(slots=True)
class Settings:
    wiki_path: Path
    title: str
    host: str
    port: int
    dark_mode: bool
    storage_secret: str

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
    )
