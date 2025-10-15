# main.py

import logging
import os
from functools import lru_cache

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from wordle_helper import WordleHelper

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize the v2 helper for the new UI
helper_v2 = WordleHelper(5)
app = FastAPI()

logger.info("Starting Wordle Aid API server")

# Add CORS middleware to allow frontend requests from any origin and with any method, including OPTIONS preflight requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/filter")
async def filter_words_v2(request: Request):
    data = await request.json()
    logger.info(f"Received filter request with data: {data}")
    filter_spec = data.get("filter_spec", {})
    filtered = helper_v2.filter_characters(filter_spec)
    return list(filtered)


@lru_cache(maxsize=128)
def _get_word_definition(word: str) -> dict:
    """
    Fetch word definition from dictionary API
    """
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch word definition")

    return response.json()


@app.get("/api/word-definition/{word}")
def get_word_definition(word: str):
    """
    Fetch word definition from dictionary API
    """
    logger.info(f"Word definition requested for: {word}")
    try:
        result = _get_word_definition(word)
        logger.info(f"Word definition served for: {word}")
        return result
    except requests.RequestException as e:
        logger.error(f"Request exception while fetching definition for '{word}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching definition: {str(e)}")
    except HTTPException:
        # Re-raise HTTPExceptions as they already contain proper error info
        raise


# Serve static files from the 'build' directory
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, ssl_keyfile=None, ssl_certfile=None)
