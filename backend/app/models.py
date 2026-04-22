from pydantic import BaseModel, Field


class Similarity(BaseModel):
    value: float = Field(
        description="Cosine similarity with the daily word", ge=-1.0, le=1.0
    )
    rank: int

    @property
    def is_target(self) -> bool:
        return self.rank == 0


class GuessResponse(BaseModel):
    word: str = Field(description="The word guessed by the player")
    score: int = Field(description="The score for the guess")
    found: bool = Field(description="Whether the player has guessed the daily word")


class VocabularyResponse(BaseModel):
    words: list[str] = Field(description="Words eligible to be the daily word")


class SimilarWord(BaseModel):
    word: str = Field(description="A word similar to the query")
    score: int = Field(description="The score for the similar word")


class SimilarWordsResponse(BaseModel):
    words: list[SimilarWord] = Field(
        description="Top similar words ordered by rank descending"
    )
