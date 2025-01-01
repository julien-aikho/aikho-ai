"""Chat agent interface and implementations."""

from typing import Optional
from pydantic import BaseModel

class ChatResponse(BaseModel):
    """Response from a chat agent."""
    content: str
    error: Optional[str] = None

class ChatRequest(BaseModel):
    """Request to a chat agent."""
    content: str
    agent_id: str
    user_id: str = "default"

class ChatAgent:
    """Base interface for chat agents. Any class that implements chat() is a valid chat agent."""
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and return a response."""
        raise NotImplementedError("Chat agents must implement chat()") 
    
    