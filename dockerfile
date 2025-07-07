# --- Build stage ---
FROM node:20-alpine AS build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* frontend/pnpm-lock.yaml* frontend/yarn.lock* ./
COPY frontend/ ./
RUN npm install && npm run build

WORKDIR /backend
COPY backend/requirements.txt ./
COPY backend/src/ ./src/
COPY backend/words_alpha.txt ./

# --- Final stage ---
FROM python:3.11-alpine
WORKDIR /app

# Copy built frontend and backend
COPY --from=build /frontend/build /app/frontend
COPY --from=build /backend /app/backend

# Install process manager
RUN apk add --no-cache nodejs npm && pip install --no-cache-dir -r /app/backend/requirements.txt

# Entrypoint script
WORKDIR /app
COPY start.sh .

EXPOSE 9191 3000

CMD ["sh", "start.sh"]