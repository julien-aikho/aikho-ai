"""Thread model for chat conversations."""

from sqlmodel import SQLModel, Field
from datetime import datetime

class Thread(SQLModel, table=True):
    """
    Represents a chat conversation thread between a user and a persona.
    Each thread is uniquely identified by the combination of user_id and persona_id.
    """
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Indexed for faster user-based queries
    persona_id: str = Field(index=True)  # Indexed for faster persona-based queries
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "default",
                "persona_id": "basic",
                "name": "Chat with basic",
                "created_at": "2024-02-20T12:00:00",
                "updated_at": "2024-02-20T12:00:00"
            }
        } 