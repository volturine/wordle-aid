# --- Backend build stage ---
FROM python:3.11-slim

# Create a custom user with UID 1234 and GID 1234
RUN addgroup --gid 1234 appgroup && adduser --uid 1234 --gid 1234 --disabled-password --gecos "" customuser 

RUN mkdir -p /home/wordle_helper
RUN mkdir -p /home/wordle_helper/frontend
RUN mkdir -p /home/wordle_helper/backend

# backend
WORKDIR /home/wordle_helper/backend
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
COPY backend/ ./

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


# Frontend
WORKDIR /home/wordle_helper/frontend
COPY frontend/ ./

# Entrypoint script
WORKDIR /home/wordle_helper
COPY start.sh .

# Fix ownership and permissions for all files
RUN chown -R customuser:appgroup /home/wordle_helper
RUN chmod -R u+rwX,g+rwX /home/wordle_helper
RUN chmod +x start.sh

USER customuser

EXPOSE 8000 3000

CMD ["sh", "start.sh"]