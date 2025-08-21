# --- Frontend build stage ---
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/ ./
ENV PUBLIC_API_BASE=http://localhost:8000
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
COPY backend/ ./

# Fix ownership and permissions for all files
RUN chown -R customuser:appgroup /home/wordle_helper
RUN chmod -R u+rwX,g+rwX /home/wordle_helper

USER customuser

EXPOSE 8000 3000

WORKDIR /home/wordle_helper/backend
CMD ["uv", "run", "src/main.py"]