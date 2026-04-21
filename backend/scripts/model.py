import logging
from pathlib import Path

import gensim.downloader as api
from gensim.models import KeyedVectors
from gensim.parsing.preprocessing import STOPWORDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_good_candidate(word: str) -> bool:
    return len(word) >= 3 and word.isalpha() and word not in STOPWORDS


def main():
    data_dir = Path(__file__).parent
    vocabulary_file = data_dir / "google-10000-english.txt"
    model_output = data_dir / "model.kv"

    with vocabulary_file.open(encoding="utf-8") as f:
        logger.info("Loading common English words from %s", vocabulary_file)
        vocabulary = [line.strip() for line in f if line.strip()]
        logger.info("Loaded %d raw words", len(vocabulary))

        logger.info("Filtering for quality...")
        filtered = [w for w in vocabulary if is_good_candidate(w)]
        logger.info("Kept %d words after quality filter", len(filtered))

        logger.info("Loading source model...")
        full_model: KeyedVectors = api.load("word2vec-google-news-300")
        logger.info("Source model vocabulary: %d words", len(full_model))

        logger.info("Intersecting with model vocabulary...")
        candidates = [w for w in filtered if w in full_model]
        logger.info("Final candidates: %d words", len(candidates))

        logger.info("Building filtered KeyedVectors...")
        filtered_kv = KeyedVectors(vector_size=full_model.vector_size)
        filtered_kv.add_vectors(
            keys=candidates,
            weights=[full_model[w] for w in candidates],
        )
        filtered_kv.save(str(model_output))
        logger.info("Saved filtered model to %s", model_output)


if __name__ == "__main__":
    main()
