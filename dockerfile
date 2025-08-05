# --- Frontend build stage ---
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/ ./
RUN npm install && npm run build

# --- Backend build stage ---
FROM python:3.11-slim AS backend-build

# Create a custom user with UID 1234 and GID 1234
RUN addgroup --gid 1234 appgroup && adduser --uid 1234 --gid 1234 --disabled-password --gecos "" customuser 

RUN mkdir -p /home/wordle_helper
RUN mkdir -p /home/wordle_helper/frontend
RUN mkdir -p /home/wordle_helper/backend

WORKDIR /home/wordle_helper/backend

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY backend/ ./
RUN uv pip install .

# Frontend
COPY --from=frontend-build /frontend /home/wordle_helper/frontend

# Set ownership recursively
RUN chown -R customuser:appgroup /home/wordle_helper

# Optional: Make sure permissions are readable/writable (adjust as needed)
RUN chmod -R u+rwX,g+rwX /home/wordle_helper

# Install process manager
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

# Entrypoint script
WORKDIR /home/wordle_helper
COPY start.sh .
RUN chown customuser:appgroup start.sh && chmod +x start.sh

# Switch to the custom user
USER customuser

EXPOSE 8000 3000

CMD ["sh", "start.sh"]