from pathlib import Path

from gensim.models import KeyedVectors


def main():
    source = Path("cc.en.300.vec")
    output = Path("model.kv")
    vocab_file = Path("vocabulary.txt")

    with vocab_file.open(encoding="utf-8") as f:
        allowed = {line.strip() for line in f if line.strip()}

    print(f"Loading full fastText model from {source}...")
    full = KeyedVectors.load_word2vec_format(str(source), binary=False, limit=500_000)
    print(f"Loaded {len(full)} words from source")

    kept = [w for w in allowed if w in full]
    print(f"Keeping {len(kept)} words after filter")

    filtered = KeyedVectors(vector_size=full.vector_size)
    filtered.add_vectors(kept, [full[w] for w in kept])

    filtered.save(str(output))
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
