# --- Frontend build stage ---
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* frontend/pnpm-lock.yaml* frontend/yarn.lock* ./
COPY frontend/ ./
RUN npm install && npm run build

# --- Backend build stage ---
FROM python:3.11-slim AS backend-build
WORKDIR /backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/src/ ./src/
COPY backend/words_alpha.txt ./

# --- Final stage ---
FROM python:3.11-slim
WORKDIR /app

# Backend
COPY --from=backend-build /backend /app/backend

# Frontend
COPY --from=frontend-build /frontend /app/frontend

# Install process manager
RUN pip install --no-cache-dir -r /app/backend/requirements.txt && apt-get update && apt-get install -y nodejs npm

# Install frontend production dependencies (if needed)
WORKDIR /app/frontend
RUN npm install --omit=dev

# Entrypoint script
WORKDIR /app
COPY start.sh .

EXPOSE 9191 3000

CMD ["sh", "start.sh"]