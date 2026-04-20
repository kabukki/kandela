import spacy
nlp = spacy.load("fr_core_news_sm")

# doc = nlp("Personne parle de musique. Je vais voir mon père.")
doc = nlp("vais")
for t in doc:
    print(t.text, "→", t.lemma_, t.pos_)
