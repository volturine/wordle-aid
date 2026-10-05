#!/usr/bin/env bash
# Build the SvelteKit frontend and stage it for the Cloudflare Worker.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND="$ROOT/frontend"
PUBLIC="$ROOT/worker/public"

(cd "$FRONTEND" && npm install && npm run build)

rm -rf "$PUBLIC"
mkdir -p "$PUBLIC"
cp -R "$FRONTEND/build/." "$PUBLIC/"

echo "Frontend staged in worker/public ($(find "$PUBLIC" -type f | wc -l | tr -d ' ') files)"
echo "Next: cd worker && uv run pywrangler deploy"
