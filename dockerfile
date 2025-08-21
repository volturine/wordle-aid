# --- Frontend build stage ---
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/ ./
RUN npm install && npm run build

# --- Backend build stage ---
FROM ghcr.io/astral-sh/uv:0.8.13-python3.13-alpine

# Create a custom user with UID 1234 and GID 1234
RUN addgroup --gid 1234 appgroup && adduser --uid 1234 --gid 1234 --disabled-password --gecos "" customuser 

RUN mkdir -p /home/wordle_helper
RUN mkdir -p /home/wordle_helper/frontend
RUN mkdir -p /home/wordle_helper/backend

WORKDIR /home/wordle_helper

# Frontend
COPY --from=frontend-build /frontend/build /home/wordle_helper/frontend

# backend
COPY backend/ ./

# Fix ownership and permissions for all files
RUN chown -R customuser:appgroup /home/wordle_helper
RUN chmod -R u+rwX,g+rwX /home/wordle_helper

USER customuser

EXPOSE 8000 3000

WORKDIR /home/wordle_helper/backend
CMD ["uv", "run", "src/main.py"]