# Hopswiki Web

A web-UI for Hopswiki — a personal cross-domain wiki spanning my three Library
areas (private reading, WDODelta work, programming/AI). Built with
[NiceGUI](https://nicegui.io/) and styled to match my personal taste
(`PAI/USER/UIDESIGNSTYLE.md`): warm dark palette, serif headings on a sans
body, sharp 0–2px corners, flat surfaces, amber / teal / magenta accents.

Sibling of [`pkw-web`](https://github.com/Hopsakee/pkw-web), which serves the
WDODelta beleid wiki in WDODelta brand colors. Same data-layer code, different
theme, different default data source, different port.

## Disclaimer

This is a **personal tool** — built AI-assisted (Claude Code) without
line-by-line manual review. There are no guarantees of security, stability, or
correctness. Do not deploy it for anyone other than yourself.

## Features

- **Wiki browser** — five categories (entities, concepts, sources, comparisons, syntheses)
- **Wikilink resolution** — `[[slug]]` and `[[slug|Display Text]]` resolve to real links
- **Backlinks + outlinks + sources** — every page shows who links to it and where it points
- **Substring search** — across titles, body text, and tags (300 ms debounce)
- **Sort + tag filter** — by name, in-links, out-links, total links; collapsible tag cloud
- **Dark / light toggle** — preference persists across pages
- **Markdown rendering** — headings, lists, tables, code, blockquotes, wikilinks

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- A wiki directory matching the five-folder schema (default: `~/Drive/Hopswiki/wiki`)

## Quick Start

```bash
git clone https://github.com/Hopsakee/hopswiki-web.git
cd hopswiki-web
uv sync
uv run main.py
```

The app starts at http://localhost:8082.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `WIKI_PATH` | `~/Drive/Hopswiki/wiki` | Wiki directory to read |
| `APP_TITLE` | `Hopswiki` | Browser tab title |
| `APP_HOST` | `0.0.0.0` | Bind address |
| `APP_PORT` | `8082` | HTTP port (pkw-web sits on 8081) |
| `DARK_MODE` | `true` | Start in dark mode |
| `STORAGE_SECRET` | `hopswiki-web-storage-secret` | NiceGUI user-storage signing key |

## Wiki Format

The same schema as [`pkw-web`](https://github.com/Hopsakee/pkw-web) and
`wiki_beleid` — five sibling folders under `wiki/`:

```
wiki/
├── entities/       # people, organizations, tools
├── concepts/       # ideas, frameworks, recurring themes
├── sources/        # one summary page per archived document
├── comparisons/    # side-by-side analyses
└── syntheses/      # cross-source theses
```

Frontmatter per file:

```yaml
---
title: "Page Title"
type: source            # entity | concept | source | comparison | synthesis
created: 2026-05-17
updated: 2026-05-17
tags: [ai, hydrology]
sources: ["another-page-slug"]
---
```

Pages are written by the `_PKW_LIBRARIAN` skill — this app is read-only.

## Project Structure

```
hopswiki-web/
├── main.py                  # Entry: loads WikiStore, registers pages, ui.run
├── pyproject.toml           # uv-managed dependencies
├── Dockerfile               # uv + Python 3.12 image
├── compose.yaml             # docker compose service (hopswiki-web)
└── app/
    ├── config.py            # Settings dataclass from env vars
    ├── wiki.py              # WikiStore: load, parse, index, backlinks
    ├── pages/
    │   ├── home.py          # Folder cards + all-pages list
    │   ├── folder.py        # Single-category listing
    │   ├── page.py          # One wiki page + sidebar
    │   ├── search.py        # Substring search
    │   └── help.py          # Hopswiki intro
    └── components/
        ├── layout.py        # Theme CSS, header, page wrapper
        ├── badges.py        # Type badges
        ├── markdown.py      # Markdown renderer with wikilink resolution
        └── page_list.py     # Shared sort + tag-filter list component
```

## Docker

```bash
docker build -t hopswiki-web .
docker run -p 8082:8080 \
  -v ~/Drive/Hopswiki/wiki:/app/data/wiki:ro \
  -e WIKI_PATH=/app/data/wiki \
  hopswiki-web
```

## Style

Theme follows `PAI/USER/UIDESIGNSTYLE.md`: warm palette (deep brown `#0e0c0a`
backgrounds, amber `#f46a25` accent, teal `#28a197` hover, magenta `#801650`
active state), serif headings on a sans body, sharp 0–2px corners, flat
surfaces (no shadows, no gradients), low contrast. Personal-taste defaults,
not WDODelta corporate identity.

## License

MIT
