#!/bin/sh
# Build frontend
cd frontend && npm install && npm run build

# Start backend
cd ../backend && uv run ./src/main.py
