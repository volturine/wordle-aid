# main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from wordle_helper import WordleHelper
from fastapi.middleware.cors import CORSMiddleware

# Initialize the v2 helper for the new UI
helper_v2 = WordleHelper(5)
app = FastAPI()

# Add CORS middleware to allow frontend requests from any origin and with any method, including OPTIONS preflight requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/filter")
async def filter_words_v2(request: Request):
    data = await request.json()
    filter_spec = data.get("filter_spec", {})
    filtered = helper_v2.filter_characters(filter_spec)
    return list(filtered)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, ssl_keyfile=None, ssl_certfile=None)
