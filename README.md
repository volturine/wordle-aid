# World Helper Project

## Structure

- `backend/` — Python backend (API, logic, word list)
- `front-end/` — SvelteKit + Tailwind frontend

See each subdirectory for details.

```bash
# Build and push backend image
USER_NAME=kripso
docker build --platform linux/amd64 -t gitea.kripso-world.com/kripso/wordle_helper .
docker push gitea.kripso-world.com/kripso/wordle_helper

```
