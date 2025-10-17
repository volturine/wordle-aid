"""
Main FastAPI application
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.v1.router import api_router
from modules.word_definition.models import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Wordle Aid API", version="1.0.0")

# Initialize database
init_db()

logger.info("Starting Wordle Aid API server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Serve static files in production
if os.getenv("PROD_MODE_ENABLED"):
    static_files_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
    app.mount("/_app", StaticFiles(directory=os.path.join(static_files_dir, "_app")), name="app")

    @app.get("/{full_path:path}")
    def serve_static_or_index(full_path: str):
        path = os.path.join(static_files_dir, full_path)
        if os.path.isfile(path):
            return FileResponse(path)
        index_path = os.path.join(static_files_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
