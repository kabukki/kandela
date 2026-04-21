import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from gensim.models import KeyedVectors

from .core import (
    WordNotFoundError,
    get_daily_word,
    get_most_similar,
    get_similarity,
    get_vocabulary,
)
from .dependencies import ModelDep
from .models import GuessResponse, SimilarWord, SimilarWordsResponse, VocabularyResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading model...")
    app.state.model = KeyedVectors.load("scripts/model.kv")
    logger.info("Model loaded", app.state.model)
    yield


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


@app.get("/vocabulary", response_model=VocabularyResponse)
async def vocabulary(model: ModelDep):
    return VocabularyResponse(words=get_vocabulary(model))


@app.get("/guess", response_model=GuessResponse)
async def guess(q: str, model: ModelDep):
    guess = q.strip().lower()
    try:
        word = get_daily_word(model, datetime.now(timezone.utc).date())
        logger.info(
            "Comparing guess '%s' to daily word '%s'",
            guess,
            word,
        )
        similarity = get_similarity(model, word, guess)
        return GuessResponse(
            word=guess,
            similarity=round(similarity.value, ndigits=4),
            found=similarity.match,
        )
    except WordNotFoundError:
        raise HTTPException(status_code=404, detail="Unknown word")


@app.get("/similar", response_model=SimilarWordsResponse)
async def similar(q: str, model: ModelDep):
    word = q.strip().lower()
    try:
        results = get_most_similar(model, word, topn=10)
        return SimilarWordsResponse(
            words=[
                SimilarWord(word=w, similarity=round(s, ndigits=4)) for w, s in results
            ],
        )
    except WordNotFoundError:
        raise HTTPException(status_code=404, detail="Unknown word")
