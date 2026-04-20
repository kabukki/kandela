from gensim.models import KeyedVectors


class WordNotFoundError(Exception):
    def __init__(self, word: str):
        self.word = word
        super().__init__(f"Word not in vocabulary: {word!r}")


def get_daily_word():
    return "house"


def get_similarity(model: KeyedVectors, a: str, b: str):
    if a not in model:
        raise WordNotFoundError(a)

    if b not in model:
        raise WordNotFoundError(b)

    if a == b:
        return 1.0

    return float(model.similarity(a, b))
