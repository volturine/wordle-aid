#!/bin/sh
# Start backend
.venv/bin/uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --log-level debug &
# Start frontend (Vite preview server as before)
cd frontend && npm run preview -- --host 0.0.0.0 --port 3000
