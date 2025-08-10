#!/bin/sh
# Start backend
cd backend && uv run ./src/main.py &

# Start frontend (Vite dev server)
cd frontend && \
npm install && \
npm run build && \
npm run dev -- --host 0.0.0.0 --port 3000
