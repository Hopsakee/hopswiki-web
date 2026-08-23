#!/usr/bin/env bash
# Sync a local wiki folder to hopsakee.top's persistent storage, then trigger
# hopswiki-web's in-process /_reload so the change is live without a restart.
#
# Manual trigger by design (2026-08-24) — no cron, no systemd. Run this from
# a machine that has ~/.ssh/sledge_wsl (or point SSH_KEY elsewhere).
#
# Usage:
#   ./sync-wiki.sh [source-dir]
# source-dir defaults to ~/Obsidian/Hopswiki/Hopswiki/ if omitted.
#
# The reload call runs INSIDE the container via `docker exec`, never through
# the public https://hopswiki.hopsakee.top/_reload URL — that domain sits
# behind Caddy's Authelia forward-auth gate, so an unauthenticated POST would
# 302 before the app's own token check ever runs. Reloading from inside the
# container talks to 127.0.0.1:8080 directly and reads the token from the
# container's own mounted secret file — the token never crosses SSH argv or
# this script's environment.
set -uo pipefail

WIKI_SRC="${1:-$HOME/Obsidian/Hopswiki/Hopswiki/}"
WIKI_SRC="${WIKI_SRC%/}/"  # normalize trailing slash for rsync semantics

SERVER="ubuntu@hopsakee.top"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/sledge_wsl}"
REMOTE_WIKI_DIR="/mnt/HC_Volume_105122334/hopswiki/wiki/"
CONTAINER="hopswiki-web"

if [ ! -d "$WIKI_SRC" ]; then
  echo "sync-wiki: source directory $WIKI_SRC does not exist, aborting" >&2
  exit 2
fi

PAGE_COUNT="$(find "$WIKI_SRC" -type f -name '*.md' 2>/dev/null | wc -l)"
if [ "$PAGE_COUNT" -eq 0 ]; then
  echo "sync-wiki: $WIKI_SRC contains zero .md files — refusing to rsync --delete against what looks like an empty or wrong source" >&2
  exit 2
fi

echo "sync-wiki: rsyncing $WIKI_SRC ($PAGE_COUNT pages) -> $SERVER:$REMOTE_WIKI_DIR"
if ! rsync -az --delete \
  --exclude='.obsidian/' \
  -e "ssh -i $SSH_KEY" \
  "$WIKI_SRC" "$SERVER:$REMOTE_WIKI_DIR"; then
  echo "sync-wiki: rsync FAILED — not calling /_reload against stale-or-partial content" >&2
  exit 1
fi

echo "sync-wiki: rsync ok, triggering /_reload inside the container"
REMOTE_PY='
import sys, urllib.request, urllib.error, pathlib
token = pathlib.Path("/run/secrets/reload_token").read_text().strip()
req = urllib.request.Request(
    "http://127.0.0.1:8080/_reload",
    method="POST",
    headers={"X-Reload-Token": token},
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(r.status, r.read().decode())
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
    sys.exit(1)
'
if ! ssh -i "$SSH_KEY" "$SERVER" \
  "docker exec $CONTAINER uv run python3 -c '$REMOTE_PY'"; then
  echo "sync-wiki: /_reload FAILED — see docker exec output above" >&2
  exit 3
fi

echo "sync-wiki: reload ok"
