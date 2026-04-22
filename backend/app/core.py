import hashlib
import math
from datetime import date

from gensim.models import KeyedVectors

from .models import Similarity


class WordNotFoundError(Exception):
    def __init__(self, word: str):
        self.word = word
        super().__init__(f"Word not in vocabulary: {word!r}")


def get_vocabulary(model: KeyedVectors) -> list[str]:
    """Returns all words in the model's vocabulary, usable as daily words."""
    return list(model.index_to_key)


def get_daily_word(model: KeyedVectors, date: date):
    vocabulary = get_vocabulary(model)
    seed = date.isoformat().encode()
    digest = hashlib.sha256(seed).digest()
    index = int.from_bytes(digest, "big") % len(vocabulary)
    return vocabulary[index]


def get_most_similar(
    model: KeyedVectors, word: str, topn: int
) -> list[tuple[str, Similarity]]:
    if word not in model:
        raise WordNotFoundError(word)

    return [
        (w, Similarity(value=float(s), rank=i + 1))
        for i, (w, s) in enumerate(model.most_similar(word, topn=topn))
    ]


def get_similarity(model: KeyedVectors, a: str, b: str):
    if a not in model:
        raise WordNotFoundError(a)

    if b not in model:
        raise WordNotFoundError(b)

    return Similarity(
        value=float(model.similarity(a, b)),
        rank=0 if a == b else int(model.rank(a, b)),
    )


def get_score(model: KeyedVectors, rank: int):
    if rank == 0:
        return 1000
    t = math.log10(rank) / math.log10(len(model.index_to_key))
    return max(0, round(999 * (1 - t)))

    # return Similarity(value=float(model.similarity(a, b)), rank=int(model.rank(a, b)))
