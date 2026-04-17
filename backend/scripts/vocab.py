import sys
from wordfreq import iter_wordlist, zipf_frequency
from gensim.models import KeyedVectors
import spacy

def main():
    print("Loading spaCy French model...", file=sys.stderr)
    nlp = spacy.load("fr_core_news_sm")
    
    print("Loading Word2Vec model...", file=sys.stderr)
    model = KeyedVectors.load_word2vec_format("frWac_no_postag_no_phrase_500_skip_cut100.bin", binary=True, unicode_errors="ignore")
    
    kept = 0
    missed = 0
    skipped = 0
    
    # Track seen lemmas to avoid duplicates
    seen_lemmas = set()
    
    for w in iter_wordlist("fr", wordlist="best"):
        doc = nlp(w)
        if len(doc) == 0:
            skipped += 1
            continue
        
        token = doc[0]
        pos_tag = token.pos_
        lemma = token.lemma_.lower()
        
        # Get zipf frequency for the original word
        zipf = zipf_frequency(w, "fr")
        
        # Only keep nouns, verbs, and adjectives
        if pos_tag not in ["NOUN", "VERB", "ADJ"]:
            skipped += 1
            continue
        
        # Skip if we've already seen this lemma
        if lemma in seen_lemmas:
            skipped += 1
            continue
        
        seen_lemmas.add(lemma)
        
        # Check if lemma is in model
        if lemma in model.key_to_index:
            print(f"✓ {w}\t{lemma}\t{pos_tag}\t{zipf:.2f}")
            kept += 1
        else:
            print(f"✗ {w}\t{lemma}\t{pos_tag}\t{zipf:.2f}")
            missed += 1
        
        if (kept + missed) % 1000 == 0:
            print(f"... processed {kept + missed}, found={kept}, missing={missed}", file=sys.stderr)
    
    print(f"\nDone. Found {kept} lemmas in model, {missed} missing, {skipped} skipped (invalid/filtered).", file=sys.stderr)

if __name__ == "__main__":
    main()
