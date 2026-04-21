import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from gensim.models import KeyedVectors

from .core import WordNotFoundError, get_daily_word, get_similarity
from .models import GuessResponse

ml_models: dict[str, KeyedVectors] = {}
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading model...")
    # app.state.
    ml_models["word2vec"] = KeyedVectors.load("data/model.kv")
    logger.info("Model loaded", ml_models["word2vec"])
    yield
    ml_models.clear()


def generate_operation_id(route: APIRoute):
    return route.name


app = FastAPI(lifespan=lifespan, generate_unique_id_function=generate_operation_id)
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
            similarity=round(similarity.value, ndigits=4),
            found=similarity.match,
        )
    except WordNotFoundError:
        raise HTTPException(status_code=404, detail="Unknown word")
