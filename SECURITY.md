# Security policy

Wordle Aid is a stateless Wordle helper: it stores no user accounts, no user
data, and sets no cookies. The only database rows are a static word dictionary
and a word-definition cache.

## Supported versions

Security fixes are applied to the latest release on `master` and to the most
recent tagged semantic version when practical. Older tags may not receive
backports.

| Version               | Supported        |
| --------------------- | ---------------- |
| Latest `master`       | Yes              |
| Latest tagged release | Yes              |
| Older tags            | Best effort only |

## What Wordle Aid stores

- **Words table** — a static English dictionary imported once at setup.
- **Definitions cache** — fetched from the WordsAPI (RapidAPI) on demand and
  cached in D1. Contains only public dictionary content.
- **No user data** — no accounts, no authentication, no session state, no
  tracking. The frontend PWA keeps its game board state in the browser only.

## What Wordle Aid does not claim

- The worker is not hardened against abuse beyond platform limits: anyone can
  call the API. Do not self-host it on a public domain expecting zero abuse.
- The RapidAPI key is a worker secret; never log it or expose it through any
  endpoint or error message.

## Reporting a vulnerability

Please report vulnerabilities privately via [GitHub Security
Advisories](https://github.com/volturine/wordle-aid/security/advisories/new) —
do not open a public issue.

Please include:

- A description of the vulnerability and its impact
- Steps to reproduce or a proof of concept
- Affected endpoints or files

We will acknowledge reports, keep the discussion private, and credit you in
the fix unless you prefer to stay anonymous.
