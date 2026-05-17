# Contributing to Hopswiki Web

Thanks for your interest in contributing to Hopswiki Web.

## Important: This Is a Vibecoded Project

This project was vibecoded — built through AI-assisted development without manual code review of every line. It is a personal tool, not production software. Treat it accordingly: it may contain rough edges, unhandled edge cases, or unconventional patterns.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (not pip, poetry, or conda)
- A wiki directory with markdown files (see README.md for format)

### Getting Started

```bash
git clone https://github.com/Hopsakee/hopswiki-web.git
cd hopswiki-web
uv sync
uv run main.py
```

### Running with Custom Wiki Path

```bash
WIKI_PATH=/path/to/your/wiki uv run main.py
```

## Code Conventions

- **Python 3.12+** with type hints throughout
- **uv** for dependency management — never add dependencies via pip
- **Pathlib** for file operations
- Keep modules focused: pages in `app/pages/`, reusable UI in `app/components/`, data logic in `app/wiki.py`
- Use CSS variables (`var(--text-primary)`, etc.) for theme-aware styling — never hardcode colors
- Test that changes work in both dark and light mode

## Making Changes

1. Create a branch: `git checkout -b your-feature`
2. Make your changes
3. Test locally: `uv run main.py` and verify in the browser
4. Check both dark and light mode
5. Commit with a descriptive message
6. Push and open a pull request

## Architecture Overview

### Data Flow

1. `WikiStore.load()` reads all `.md` files from disk at startup
2. Frontmatter is parsed, wikilinks extracted, backlinks computed
3. All indexes (sorted pages, tag lists, stats) are precomputed once
4. NiceGUI page handlers read from the store — no disk I/O per request

### Key Modules

| Module | Responsibility |
|--------|---------------|
| `app/wiki.py` | Data model, file parsing, indexing |
| `app/config.py` | Environment variable configuration |
| `app/components/layout.py` | Shared layout, CSS theme, header |
| `app/components/page_list.py` | Sortable/filterable page list |
| `app/components/markdown.py` | Markdown rendering with wikilink resolution |
| `app/components/badges.py` | Theme-aware type badges |
| `app/pages/*.py` | Route handlers (one file per page) |

### Theming

The app uses CSS variables scoped to `body.body--dark` and `body.body--light`. NiceGUI's `ui.dark_mode()` toggles the body class; all styling reacts via CSS variables. When adding new UI, always use `var(--text-primary)`, `var(--bg-card)`, etc. — see `layout.py` for the full variable list.

## Reporting Issues

Open an issue on GitHub with:
- What you expected
- What happened instead
- Browser and OS
- Screenshot if it's a visual issue
