# --- Frontend build stage ---
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* frontend/pnpm-lock.yaml* frontend/yarn.lock* ./
COPY frontend/ ./
RUN npm install && npm run build

# --- Backend stage ---
FROM python:3.11-slim AS backend
WORKDIR /backend

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/src/ ./src/
COPY backend/words_alpha.txt ./

# Copy built frontend to backend static directory
COPY --from=frontend-build /frontend/build ./static

# (Optional) If using FastAPI, make sure to mount ./static as StaticFiles in your backend code

ENV PYTHONPATH=/backend/src

EXPOSE 9191

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9191"]