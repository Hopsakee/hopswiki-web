"""Custom markdown renderer with wikilink support."""

from __future__ import annotations

import re
from html import escape
from typing import TYPE_CHECKING

import markdown as md

from app.wiki import WIKILINK_RE

if TYPE_CHECKING:
    from app.wiki import WikiStore

_MD = md.Markdown(extensions=["tables", "fenced_code", "nl2br"])


def render_wiki_markdown(content: str, store: WikiStore) -> str:
    """Convert wiki markdown to HTML, resolving [[wikilinks]] to real links."""

    def replace_wikilink(match: re.Match) -> str:
        slug = match.group(1).strip()
        display = match.group(2) or slug.replace("-", " ").title()
        resolved = store.resolve_slug(slug)
        if resolved:
            folder, s = resolved
            return f'<a href="/wiki/{folder}/{escape(s)}" class="wikilink">{escape(display)}</a>'
        return f'<span class="wikilink-broken">{escape(display)}</span>'

    processed = WIKILINK_RE.sub(replace_wikilink, content)
    _MD.reset()
    return _MD.convert(processed)
