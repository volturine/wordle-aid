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

# Create a custom user with UID 1234 and GID 1234
RUN addgroup --gid 1234 appgroup && adduser --uid 1234 --gid 1234 --disabled-password --gecos "" customuser 

RUN mkdir -p /home/wordle_helper

WORKDIR /home/wordle_helper

# Backend
COPY --from=backend-build /backend /home/wordle_helper/backend

# Frontend
COPY --from=frontend-build /frontend /home/wordle_helper/frontend

# Set ownership recursively
RUN chown -R customuser:appgroup /home/wordle_helper

# Optional: Make sure permissions are readable/writable (adjust as needed)
RUN chmod -R u+rwX,g+rwX /home/wordle_helper

# Set PYTHONPATH for backend imports
ENV PYTHONPATH=/home/wordle_helper/backend/src

# Install process manager
RUN pip install --no-cache-dir -r /home/wordle_helper/backend/requirements.txt
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
WORKDIR /home/wordle_helper/frontend
RUN npm install --omit=dev && npm install @tailwindcss/vite --save-dev

# Entrypoint script
WORKDIR /home/wordle_helper
COPY start.sh .
RUN chown customuser:appgroup start.sh && chmod +x start.sh

# Switch to the custom user
USER customuser

EXPOSE 8000 3000

CMD ["sh", "start.sh"]
