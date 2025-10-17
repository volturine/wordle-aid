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

WORKDIR /home/wordle_helper/database
COPY database/words.db ./
COPY database/word_definitions.db ./

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
RUN chown -R customuser:appgroup /home/wordle_helper
RUN chmod -R u+rwX,g+rwX /home/wordle_helper

USER customuser

EXPOSE 8000 3000

WORKDIR /home/wordle_helper/backend
CMD ["uv", "run", "main.py"]