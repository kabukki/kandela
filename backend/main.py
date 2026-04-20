from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from gensim.models import KeyedVectors
from models import GuessResponse
from similarity import get_similarity

ml_models: dict[KeyedVectors] = {}
target = "house"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading model...")
    ml_models["word2vec"] = KeyedVectors.load("scripts/model.kv")
    print("Model loaded", ml_models["word2vec"])
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


@app.get("/word")
async def word():
    return target


@app.get("/guess", response_model=GuessResponse)
async def guess(q: str):
    word = q.strip().lower()
    try:
        similarity = round(100 * get_similarity(ml_models["word2vec"], target, word))
        return GuessResponse(
            word=word,
            similarity=similarity,
            found=similarity == 100,
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Unknown word")
