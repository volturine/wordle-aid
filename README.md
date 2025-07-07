# World Helper Project

## Structure

- `backend/` — Python backend (API, logic, word list)
- `front-end/` — SvelteKit + Tailwind frontend

See each subdirectory for details.

```bash
USER_NAME=kripso
# unique uuid
UUID=$(uuidgen)
UUID=$(echo "$UUID" | tr '[:upper:]' '[:lower:]')
# Define the base image name
IMAGE_NAME=gitea.kripso-world.com/${USER_NAME}/wordle_helper
# echo ${IMAGE_NAME}
# echo ${UUID}

# Build the image with the UUID tag
docker build --platform linux/amd64 -t ${IMAGE_NAME}:${UUID} .

# Tag the same image as 'latest'
docker tag ${IMAGE_NAME}:${UUID} ${IMAGE_NAME}:latest

# Push both tags
docker push ${IMAGE_NAME}:${UUID}
docker push ${IMAGE_NAME}:latest

```
