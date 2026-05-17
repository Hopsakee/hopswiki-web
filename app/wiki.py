"""Wiki data loading: scan folders, parse frontmatter, compute links."""

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

import frontmatter

WIKI_FOLDERS = ("entities", "concepts", "sources", "comparisons", "syntheses")

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

_HEADING_RE = re.compile(r"^#+\s+.*$", re.MULTILINE)

TYPE_CONFIG: dict[str, dict[str, str]] = {
    "entity":     {"icon": "\U0001F464", "color": "#28a197"},
    "concept":    {"icon": "\U0001F4A1", "color": "#f46a25"},
    "source":     {"icon": "\U0001F4C4", "color": "#a285d1"},
    "comparison": {"icon": "\u2696\ufe0f", "color": "#801650"},
    "synthesis":  {"icon": "\U0001F9EC", "color": "#6bbce6"},
}

FOLDER_TO_TYPE = {
    "entities": "entity",
    "concepts": "concept",
    "sources": "source",
    "comparisons": "comparison",
    "syntheses": "synthesis",
}


def _make_snippet(content: str, max_len: int = 200) -> str:
    text = _HEADING_RE.sub("", content).strip()
    text = WIKILINK_RE.sub(r"\1", text)
    return text[:max_len] + "..." if len(text) > max_len else text


@dataclass(slots=True)
class WikiPage:
    slug: str
    folder: str
    title: str
    type: str
    created: str
    updated: str
    tags: list[str]
    sources: list[str]
    content: str
    snippet: str = ""
    outlinks: list[str] = field(default_factory=list)
    backlinks: list[str] = field(default_factory=list)
    _title_lower: str = ""
    _content_lower: str = ""
    _tags_lower: list[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"/wiki/{self.folder}/{self.slug}"


@dataclass(slots=True)
class WikiStats:
    total_pages: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    total_links: int = 0


class WikiStore:
    """Loads and indexes all wiki pages from disk."""

    def __init__(self, wiki_path: Path) -> None:
        self.wiki_path = wiki_path
        self.pages: dict[str, WikiPage] = {}
        self._slug_to_folder: dict[str, str] = {}
        self._folder_pages: dict[str, list[WikiPage]] = {}
        self._all_pages: list[WikiPage] = []
        self._all_tags: list[str] = []
        self._stats: WikiStats | None = None

    def load(self) -> None:
        self.pages.clear()
        self._slug_to_folder.clear()
        backlink_sets: dict[str, set[str]] = {}

        for folder_name in WIKI_FOLDERS:
            folder = self.wiki_path / folder_name
            if not folder.is_dir():
                continue
            for md_file in sorted(folder.glob("*.md")):
                page = self._parse_file(md_file, folder_name)
                if page:
                    key = f"{folder_name}/{page.slug}"
                    self.pages[key] = page
                    self._slug_to_folder[page.slug] = folder_name
                    backlink_sets[key] = set()

        self._compute_backlinks(backlink_sets)
        self._precompute_indexes()

    def _parse_file(self, path: Path, folder_name: str) -> WikiPage | None:
        try:
            post = frontmatter.load(str(path))
        except Exception as e:
            logger.warning("Failed to parse %s: %s", path, e)
            return None

        slug = path.stem
        meta = post.metadata
        wiki_type = FOLDER_TO_TYPE.get(folder_name, folder_name)
        content = post.content

        outlinks = [m[0] for m in WIKILINK_RE.findall(content)]

        return WikiPage(
            slug=slug,
            folder=folder_name,
            title=meta.get("title", slug.replace("-", " ").title()),
            type=meta.get("type", wiki_type),
            created=str(meta.get("created", "")),
            updated=str(meta.get("updated", "")),
            tags=(tags := [str(t) for t in (meta.get("tags", []) or [])]),
            sources=meta.get("sources", []) or [],
            content=content,
            snippet=_make_snippet(content),
            outlinks=outlinks,
            _title_lower=meta.get("title", slug.replace("-", " ").title()).lower(),
            _content_lower=content.lower(),
            _tags_lower=[t.lower() for t in tags],
        )

    def _compute_backlinks(self, backlink_sets: dict[str, set[str]]) -> None:
        for page in self.pages.values():
            for link_slug in page.outlinks:
                folder = self._slug_to_folder.get(link_slug)
                if folder:
                    target_key = f"{folder}/{link_slug}"
                    if target_key in backlink_sets:
                        backlink_sets[target_key].add(page.slug)

        for key, slugs in backlink_sets.items():
            if slugs:
                self.pages[key].backlinks = sorted(slugs)

    def _precompute_indexes(self) -> None:
        self._all_pages = sorted(self.pages.values(), key=lambda p: p._title_lower)
        for folder_name in WIKI_FOLDERS:
            self._folder_pages[folder_name] = sorted(
                [p for p in self.pages.values() if p.folder == folder_name],
                key=lambda p: p._title_lower,
            )
        folder_counts = Counter(p.folder for p in self.pages.values())
        total_links = sum(len(p.outlinks) for p in self.pages.values())
        self._stats = WikiStats(
            total_pages=len(self.pages),
            counts=dict(folder_counts),
            total_links=total_links,
        )
        tag_set: set[str] = set()
        for p in self.pages.values():
            tag_set.update(str(t) for t in p.tags)
        self._all_tags = sorted(tag_set)

    def get_page(self, folder: str, slug: str) -> WikiPage | None:
        return self.pages.get(f"{folder}/{slug}")

    def get_folder_pages(self, folder: str) -> list[WikiPage]:
        return self._folder_pages.get(folder, [])

    def get_all_pages(self) -> list[WikiPage]:
        return self._all_pages

    def get_stats(self) -> WikiStats:
        return self._stats or WikiStats()

    def get_all_tags(self) -> list[str]:
        return self._all_tags

    def search(self, query: str) -> list[WikiPage]:
        q = query.lower()
        return [
            p for p in self._all_pages
            if q in p._title_lower
            or q in p._content_lower
            or any(q in t for t in p._tags_lower)
        ]

    def resolve_slug(self, slug: str) -> tuple[str, str] | None:
        folder = self._slug_to_folder.get(slug)
        if folder:
            return folder, slug
        return None
