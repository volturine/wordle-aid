# --- Frontend build stage ---
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/ ./
RUN npm install && npm run build

# --- Backend build stage ---
FROM python:3.11-slim

# Create a custom user with UID 1234 and GID 1234
RUN addgroup --gid 1234 appgroup && adduser --uid 1234 --gid 1234 --disabled-password --gecos "" customuser 

WORKDIR /home/wordle_helper

# Frontend
COPY --from=frontend-build /frontend/build /home/wordle_helper/frontend/build

# backend
WORKDIR /home/wordle_helper/backend
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files first for better caching
COPY backend/pyproject.toml backend/uv.lock ./

# Copy source code and data files
COPY backend/api/ ./api/
COPY backend/modules/ ./modules/
COPY backend/app.py ./
COPY backend/words.db ./
COPY backend/word_definitions.db ./

# Fix ownership and permissions for all files
RUN chown -R customuser:appgroup /home/wordle_helper
RUN chmod -R u+rwX,g+rwX /home/wordle_helper

# Set environment variables for database paths
ENV WORDS_DB_PATH=/home/wordle_helper/backend/words.db
ENV WORD_DEFINITIONS_DB_PATH=/home/wordle_helper/backend/word_definitions.db

USER customuser

EXPOSE 8000 3000

WORKDIR /home/wordle_helper/backend
CMD ["uv", "run", "app.py"]