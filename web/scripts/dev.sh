#!/usr/bin/env sh
# Avoid stale webpack chunks (e.g. Cannot find module './819.js') from mixing build + dev output.
set -e
cd "$(dirname "$0")/.."

if lsof -ti :3000 >/dev/null 2>&1; then
  echo "Stopping process on port 3000..."
  lsof -ti :3000 | xargs kill -9 2>/dev/null || true
  sleep 1
fi

rm -rf .next
echo "Starting Next.js dev (clean .next)..."
exec npm run dev
