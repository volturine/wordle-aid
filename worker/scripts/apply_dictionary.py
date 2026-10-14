#!/usr/bin/env python3
"""Apply the reviewed dictionary to D1 when the bank version differs.

Usage:
    python scripts/apply_dictionary.py <database-name> --remote
    python scripts/apply_dictionary.py <database-name> --local

Schema changes are idempotent. The replacement deletes dictionary rows and
inserts the current bank. It does not read or write the definitions table.
"""
import json
import subprocess
import sys
from pathlib import Path

WORKER = Path(__file__).resolve().parents[1]
ROOT = WORKER.parent
BANK = json.loads((ROOT / 'database' / 'bank' / 'bank.json').read_text(encoding='utf-8'))


def wrangler_json(database: str, remote: bool, command: str | None = None, file: Path | None = None):
    cmd = ['npx', 'wrangler', 'd1', 'execute', database, '--remote' if remote else '--local', '--json']
    if command is not None:
        cmd.extend(['--command', command])
    if file is not None:
        cmd.extend(['--file', str(file)])
    completed = subprocess.run(cmd, cwd=WORKER, check=True, capture_output=True, text=True)
    start = completed.stdout.find('[')
    if start < 0:
        start = completed.stdout.find('{')
    if start < 0:
        raise SystemExit(completed.stdout or completed.stderr)
    payload = json.loads(completed.stdout[start:])
    if isinstance(payload, list):
        payload = payload[0]
    return payload.get('results') or []


def column_names(database: str, remote: bool) -> set[str]:
    return {row['name'] for row in wrangler_json(database, remote, command='PRAGMA table_info(words)')}


def current_version(database: str, remote: bool) -> str | None:
    rows = wrangler_json(database, remote, command='SELECT version FROM bank_meta WHERE id = 1')
    if not rows:
        return None
    return rows[0].get('version')


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in {'--remote', '--local'}:
        raise SystemExit('usage: apply_dictionary.py <database-name> --remote|--local')
    database = sys.argv[1]
    remote = sys.argv[2] == '--remote'
    wrangler_json(database, remote, file=WORKER / 'migrations' / '0000_schema.sql')
    if 'is_answer' not in column_names(database, remote):
        wrangler_json(
            database,
            remote,
            command='ALTER TABLE words ADD COLUMN is_answer INTEGER NOT NULL DEFAULT 0',
        )
    version = current_version(database, remote)
    if version == BANK['version']:
        print(f'{database} already has bank {version}')
        return
    print(f'Replacing {database} bank {version or "(none)"} with {BANK["version"]}')
    wrangler_json(database, remote, file=WORKER / 'migrations' / 'replace_dictionary.sql')
    print(f'{database} dictionary replaced')


if __name__ == '__main__':
    main()
