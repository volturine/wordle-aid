#!/usr/bin/env bash
# One-time migration: local SQLite -> Cloudflare D1
# Assumes you have already: npm i -g wrangler  (or use pywrangler/npx) and are logged in.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "1. Exporting local SQLite data to SQL migrations..."
python3 scripts/export_db.py --lengths 5
# Use '--lengths 3 4 5 6 ...' to import the full dictionary instead.

echo
echo "2. Creating the D1 database..."
npx wrangler d1 create wordle-aid || true
# Copy the printed database_id into wrangler.toml before continuing.

echo
echo "3. Applying schema + data to remote D1..."
npx wrangler d1 execute wordle-aid --remote --file migrations/0001_words.sql
npx wrangler d1 execute wordle-aid --remote --file migrations/0002_definitions.sql

echo
echo "4. Applying to LOCAL D1 (for 'pywrangler dev')..."
npx wrangler d1 execute wordle-aid --local --file migrations/0001_words.sql
npx wrangler d1 execute wordle-aid --local --file migrations/0002_definitions.sql

echo
echo "5. Setting the RapidAPI secret..."
npx wrangler secret put RAPID_API_KEY

echo "Done. Verify with:"
echo "  npx wrangler d1 execute wordle-aid --remote --command 'SELECT COUNT(*) FROM words'"
