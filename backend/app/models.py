from pydantic import BaseModel, Field


class GuessResponse(BaseModel):
    word: str = Field(description="The word guessed by the player")
    similarity: float = Field(
        description="Cosine similarity with the daily word", ge=0.0, le=1.0
    )
    found: bool = Field(description="Whether the player has guessed the daily word")
