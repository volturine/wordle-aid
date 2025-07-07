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

# Set PYTHONPATH for backend imports
ENV PYTHONPATH=/app/backend/src

# Install process manager
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    ca-certificates
rm -rf /var/lib/apt/lists/*
rm -rf /var/cache/apt/*
rm -rf /tmp/*
rm -rf /var/tmp/*
apt-get autoremove -y
apt-get autoclean
EOF


# Install frontend production dependencies (if needed)
WORKDIR /app/frontend
RUN npm install --omit=dev && npm install @tailwindcss/vite --save-dev

# Entrypoint script
WORKDIR /app
COPY start.sh .

EXPOSE 8000 3000 9193

CMD ["sh", "start.sh"]