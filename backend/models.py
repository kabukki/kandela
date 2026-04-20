from pydantic import BaseModel, Field


class GuessResponse(BaseModel):
    word: str = Field(description="The word guessed by the player")
    similarity: int = Field(
        description="Cosine similarity with the daily word", ge=0, le=100
    )
    found: bool = Field(description="Whether the player has guessed the daily word")
