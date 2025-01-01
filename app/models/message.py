"""Models for storing chat messages and their parts."""

from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship

class MessageKind(str, Enum):
    """Type of message."""
    REQUEST = "request"
    RESPONSE = "response"

class MessagePart(SQLModel, table=True):
    """Base class for all message parts."""
    id: int = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="message.id", index=True)
    part_kind: str = Field(index=True)  # Discriminator field
    content: str | None = None
    timestamp: datetime | None = Field(default=None)
    
    # Tool-specific fields
    tool_name: str | None = Field(default=None, index=True)
    tool_call_id: str | None = Field(default=None, index=True)
    args_json: str | None = Field(default=None, sa_column=Column(JSON))

    # For retry prompts
    error_details: list[dict] | None = Field(default=None, sa_column=Column(JSON))

    # Relationship
    message: "Message" = Relationship(back_populates="parts")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "message_id": 1,
                "part_kind": "user-prompt",
                "content": "Roll a dice for me",
                "timestamp": "2024-02-20T12:00:00",
                "tool_name": None,
                "tool_call_id": None,
                "args_json": None,
                "error_details": None
            }
        }

class Message(SQLModel, table=True):
    """A message in a conversation (request or response)."""
    id: int = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="thread.id", index=True)
    kind: MessageKind = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    parts: list[MessagePart] = Relationship(back_populates="message")

    def to_model_message(self) -> dict:
        """Convert to pydantic-ai ModelMessage format."""
        return {
            "kind": self.kind.value,
            "timestamp": self.timestamp,
            "parts": [
                {
                    "part_kind": p.part_kind,
                    "content": p.content,
                    "timestamp": p.timestamp,
                    "tool_name": p.tool_name,
                    "tool_call_id": p.tool_call_id,
                    "args": {"args_json": p.args_json} if p.args_json else None,
                    "error_details": p.error_details
                } for p in self.parts
            ]
        }

    @classmethod
    def from_model_message(cls, thread_id: int, msg: dict) -> "Message":
        """Create from pydantic-ai ModelMessage."""
        message = cls(
            thread_id=thread_id,
            kind=MessageKind(msg["kind"]),
            timestamp=msg.get("timestamp", datetime.utcnow()),
        )
        
        message.parts = [
            MessagePart(
                message_id=message.id,
                part_kind=p["part_kind"],
                content=p.get("content"),
                timestamp=p.get("timestamp"),
                tool_name=p.get("tool_name"),
                tool_call_id=p.get("tool_call_id"),
                args_json=p.get("args", {}).get("args_json"),
                error_details=p.get("error_details")
            ) for p in msg["parts"]
        ]
        
        return message

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "thread_id": 1,
                "kind": "request",
                "timestamp": "2024-02-20T12:00:00"
            }
        } 