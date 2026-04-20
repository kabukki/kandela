import logging
import math
from contextlib import asynccontextmanager

from core import WordNotFoundError, get_daily_word, get_similarity
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from gensim.models import KeyedVectors
from models import GuessResponse

ml_models: dict[str, KeyedVectors] = {}
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading model...")
    ml_models["word2vec"] = KeyedVectors.load("data/model.kv")
    logger.info("Model loaded", ml_models["word2vec"])
    yield
    ml_models.clear()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/guess", response_model=GuessResponse)
async def guess(q: str):
    word = q.strip().lower()
    try:
        similarity = get_similarity(ml_models["word2vec"], get_daily_word(), word)
        return GuessResponse(
            word=word,
            similarity=round(100 * similarity),
            found=math.isclose(similarity, 1.0),
        )
    except WordNotFoundError:
        raise HTTPException(status_code=404, detail="Unknown word")
