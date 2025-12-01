# --- Frontend build stage ---
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/ ./
RUN npm install && npm run build

# --- Backend build stage ---
FROM python:3.11-slim

# Create a custom user with UID 1000 and GID 1000
RUN addgroup --gid 1000 appgroup && adduser --uid 1000 --gid 1000 --disabled-password --gecos "" appuser

WORKDIR /home/wordle_helper

# Frontend
COPY --from=frontend-build /frontend/build /home/wordle_helper/frontend/build

# Create database directory for volume mount
WORKDIR /home/wordle_helper/database

# Copy initial database file (will be used if volume is empty)
COPY database/words.db ./words.db

# backend
WORKDIR /home/wordle_helper/backend
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files first for better caching
COPY backend/pyproject.toml backend/uv.lock ./

# Copy source code and data files
COPY backend/api/ ./api/
COPY backend/modules/ ./modules/
COPY backend/main.py ./main.py

# Fix ownership and permissions for all files
RUN chown -R appuser:appgroup /home/wordle_helper

USER appuser

EXPOSE 8000
VOLUME /home/wordle_helper/database

WORKDIR /home/wordle_helper/backend
CMD ["uv", "run", "main.py"]