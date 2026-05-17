#!/bin/bash
# Deploy hopswiki-web on Hetzner VM
# Run from: ~/hopsakee-server/server_setup/
ADIR="$HOME/apps"
IDIR="$ADIR/hopswiki-web"
CDIR="$HOME/hopsakee-server/config/hopswiki-web"

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

# Clone or update the app
if [ -d "$IDIR" ]; then
  cd "$IDIR" && git fetch origin && git reset --hard origin/main
else
  cd "$ADIR" && git clone https://github.com/Hopsakee/hopswiki-web.git
fi

# Build and start
cd "$CDIR"
docker compose up --build -d
