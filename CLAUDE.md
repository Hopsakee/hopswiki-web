# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

## Commands

```bash
uv sync              # Install dependencies
uv run main.py       # Start dev server at http://localhost:8082
uv run pytest        # Run tests (none exist yet)

# With a custom wiki path
WIKI_PATH=/path/to/wiki uv run main.py

# Docker
docker build -t hopswiki-web .
docker run -p 8082:8080 -v /path/to/wiki:/app/data/wiki:ro -e WIKI_PATH=/app/data/wiki hopswiki-web
```

## Architecture

NiceGUI web app (Python 3.12, Quasar/Vue underneath) that reads a local
directory of markdown files with YAML frontmatter and serves them as a wiki
with cross-references. Sibling of `pkw-web`; same data-layer code, personal
theme instead of WDODelta theme.

### Data flow

1. `WikiStore.load()` scans the five wiki folders (`entities/`, `concepts/`, `sources/`, `comparisons/`, `syntheses/`), parses frontmatter + wikilinks, computes backlinks, and precomputes all indexes **once at startup**.
2. Page handlers read from the in-memory store — no disk I/O per request.
3. `render_wiki_markdown()` resolves `[[slug]]` and `[[slug|display]]` wikilinks to HTML at render time.

### Page registration pattern

Each module under `app/pages/` exports `register(store, settings)` which
decorates handlers with `@ui.page("/path")`. All five are registered in
`main.py`.

### Theming

All colors live in CSS custom properties defined in `layout.py`'s `APP_CSS`.
Two scopes: `:root, body.body--dark` (dark, the default) and `body.body--light`
(light). NiceGUI's `ui.dark_mode()` toggles the body class. Dark-mode
preference persists via `app.storage.user["dark_mode"]`.

The palette is personal — `PAI/USER/UIDESIGNSTYLE.md`. Warm dark backgrounds
(`#0e0c0a` ... `#1a1612`), serif headings (`Georgia`, `Instrument Serif`,
`Playfair Display`), sharp 0–2px corners, flat surfaces (no `box-shadow`, no
`linear-gradient`), low contrast.

Accent colors lifted from the UIDESIGNSTYLE named palette:

| Use | Hex | rgb |
|---|---|---|
| accent (amber/burnt orange) | `#f46a25` | `rgb(244, 106, 37)` |
| accent hover (teal) | `#28a197` | `rgb(40, 161, 151)` |
| active tag (magenta) | `#801650` | `rgb(128, 22, 80)` |
| source badge (violet) | `#a285d1` | `rgb(162, 133, 209)` |
| synthesis badge (sky) | `#6bbce6` | `rgb(107, 188, 230)` |

No WDODelta brand colors anywhere — those are reserved for `pkw-web`.

### Key variables for card content

Cards (`wiki-card`) use `--bg-card` as background. Use `--card-text` and
`--card-text-muted` for text inside cards — not `--text-primary`, which is for
page-level content.

## Conventions

- **uv only** — never `pip`. Personal-script substrate is Python + uv.
- **CSS variables for all colors** — never hardcode a hex inside a `.classes()` / `.style()` call; reference `var(--*)`.
- **Test both dark and light mode** after any visual change.
- **Type hints** throughout.
- **Pathlib** for file operations.
- Pages live in `app/pages/`, reusable UI in `app/components/`, data logic in `app/wiki.py`.
- Default port `8082` (avoid colliding with `pkw-web`'s 8081).

## Deployment

Designed to run on the Hetzner VM (`hopsakee-server`) behind Caddy + Authelia.
Wiki data mounted read-only. Config goes at
`~/hopsakee-server/config/hopswiki-web/`. Deploy via `deploy.sh`.

## Refresh Contract — rsync new wiki content, then restart

`WikiStore.load()` runs ONCE at process startup. New files arriving in the
bind-mount source are visible from inside the container but the in-memory
`store.pages` dict is frozen at boot. After every meaningful rsync the
container has to be restarted:

```bash
# Both sides reference wiki/ explicitly — symmetric trailing slashes:
rsync -avh --delete -e 'ssh -i ~/.ssh/sledge_wsl' \
  ~/Drive/Hopswiki/wiki/ \
  ubuntu@hopsakee.top:/mnt/HC_Volume_105122334/hopswiki/wiki/

ssh -i ~/.ssh/sledge_wsl ubuntu@hopsakee.top 'docker restart hopswiki-web'
```

A `/_reload` endpoint avoids the container restart:

```bash
curl -fsS -X POST -H "X-Reload-Token: $RELOAD_TOKEN" \
  https://hopswiki.hopsakee.top/_reload
```

The handler rebuilds the wiki store into a fresh `WikiStore`, then atomically
swaps the in-memory state on the live store. On `load()` failure the previous
state is left untouched and the endpoint returns 500. Success returns JSON
with `status`, `pages`, `delta`, `elapsed_ms`, and `loaded_at`.

**Operator note:** `RELOAD_TOKEN` MUST be set in the deployed env (e.g. the
`hopswiki-web` compose `environment:` block on the Hetzner VM). When unset
the endpoint returns 503 on every call. Tokens shorter than 16 chars trigger
a startup warning. The token is read at startup and stripped of surrounding
whitespace; `X-Reload-Token` header is compared via `hmac.compare_digest`.

**Authelia note:** the public URL is gated by Authelia (`one_factor` policy
on `hopswiki.hopsakee.top`). External `curl` from a nightly script will hit
the Authelia redirect first. The intended deploy pattern is either an
Authelia bypass rule on `/_reload` (the handler's own token check stays the
load-bearing security layer), or invoking the curl from inside the Hetzner
VM via SSH against the internal docker network. That choice is owned by the
sibling nightly-rsync-script project.

## Vibecoded

This project was AI-assisted without line-by-line manual review. It is a
personal tool, not production software.
