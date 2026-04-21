import hashlib
from datetime import date
from typing import NamedTuple

from gensim.models import KeyedVectors


class WordNotFoundError(Exception):
    def __init__(self, word: str):
        self.word = word
        super().__init__(f"Word not in vocabulary: {word!r}")


class Similarity(NamedTuple):
    value: float
    match: bool


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
    model: KeyedVectors, word: str, topn: int = 10
) -> list[tuple[str, float]]:
    if word not in model:
        raise WordNotFoundError(word)

    return [(w, float(s)) for w, s in model.most_similar(word, topn=topn)]


def get_similarity(model: KeyedVectors, a: str, b: str):
    if a not in model:
        raise WordNotFoundError(a)

    if b not in model:
        raise WordNotFoundError(b)

    return Similarity(value=float(model.similarity(a, b)), match=(a == b))
