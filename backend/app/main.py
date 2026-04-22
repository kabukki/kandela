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
    get_score,
    get_similarity,
    get_vocabulary,
)
from .dependencies import ModelDep, get_settings
from .models import GuessResponse, SimilarWord, SimilarWordsResponse, VocabularyResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading model...")
    app.state.model = KeyedVectors.load("scripts/model.kv")
    logger.info("Model loaded")
    yield


def generate_operation_id(route: APIRoute):
    return route.name


settings = get_settings()
app = FastAPI(lifespan=lifespan, generate_unique_id_function=generate_operation_id)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/vocabulary", response_model=VocabularyResponse)
async def vocabulary(model: ModelDep):
    return VocabularyResponse(words=get_vocabulary(model))


@app.post("/guess", response_model=GuessResponse)
async def guess(q: str, model: ModelDep):
    try:
        guess = q.strip().lower()
        word = get_daily_word(model, datetime.now(timezone.utc).date())
        similarity = get_similarity(model, word, guess)
        score = get_score(model, similarity.rank)

        logger.info(
            "guess='%s' target='%s' rank=%d score=%d",
            guess,
            word,
            similarity.rank,
            score,
        )

        return GuessResponse(word=guess, score=score, found=(similarity.is_target))
    except WordNotFoundError as e:
        if e.word == guess:
            raise HTTPException(status_code=404, detail="Unknown word")
        logger.error(f"Daily word {e.word!r} not found in model")
        raise HTTPException(status_code=500, detail="Server vocabulary error")


@app.get("/similar", response_model=SimilarWordsResponse)
async def similar(q: str, model: ModelDep):
    word = q.strip().lower()
    try:
        results = get_most_similar(model, word, topn=10)
        return SimilarWordsResponse(
            words=[
                SimilarWord(
                    word=word,
                    score=get_score(model, similarity.rank),
                )
                for word, similarity in results
            ],
        )
    except WordNotFoundError:
        raise HTTPException(status_code=404, detail="Unknown word")
