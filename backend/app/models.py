from pydantic import BaseModel, Field


class GuessResponse(BaseModel):
    word: str = Field(description="The word guessed by the player")
    similarity: float = Field(
        description="Cosine similarity with the daily word", ge=-1.0, le=1.0
    )
    found: bool = Field(description="Whether the player has guessed the daily word")


class VocabularyResponse(BaseModel):
    words: list[str] = Field(description="Words eligible to be the daily word")


class SimilarWord(BaseModel):
    word: str = Field(description="A word similar to the query")
    similarity: float = Field(
        description="Cosine similarity with the query word", ge=0.0, le=1.0
    )


class SimilarWordsResponse(BaseModel):
    words: list[SimilarWord] = Field(
        description="Top similar words ordered by similarity descending"
    )
