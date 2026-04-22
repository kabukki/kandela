# 🕯️ kandela

Guess the daily word using semantic similarity

[→ Play today's puzzle!](https://kandela.le-roux.dev)

## How it works

Each day, a single word is chosen. Your goal is to find it.
 
Every guess you make is scored by **semantic similarity** to the mystery word (how close their meanings are), computed via cosine distance on word embeddings. Guesses appear in a dark playfield, positioned radially around a central star: the closer your word's meaning, the closer it orbits the center. A distant guess drifts to the edge and fades; a close one burns bright near the flame.
 
When you win, the star reveals the target word and the closest neighbors bloom into the constellation, showing you the full semantic neighborhood you were exploring in the dark.

> Scores are expressed in **candelas (cd)**, a nod to the SI unit of luminous intensity. A guess of 100 cd means you've found it.

## Stack

**Frontend** — React, [d3-force](https://github.com/d3/d3-force) for the constellation physics, Tailwind CSS. Hosted on Cloudflare.
 
**Backend** — FastAPI, pre-computed word embeddings loaded in memory at startup. Hosted on Railway.

## Development

```bash
# backend
cd backend
uv run fastapi dev

# frontend
cd frontend
npm install
npm start
```

## Credits

Kandela stands on the shoulders of the daily semantic word game genre, pioneered by:
 
- [Semantle](https://semantle.com/) by David Turner
- [Cémantix](https://cemantix.certitudes.org/) by Nicolas Lenormand
- [Contexto](https://contexto.me/) by Bruno Martins

### Word lists
 
- [wordfreq](https://github.com/rspeer/wordfreq)

### Embedding models
 
- [word2vec](https://code.google.com/archive/p/word2vec/)
- [GloVe](https://nlp.stanford.edu/projects/glove/)
- [fastText](https://fasttext.cc/docs/en/english-vectors.html)
