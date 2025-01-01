"""Basic chat agent implementation."""

import logfire
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from app.agents.chat import ChatAgent, ChatRequest, ChatResponse
from app.config import get_settings

class BasicAgent(ChatAgent):
    """A basic chat agent."""
    
    def __init__(self):
        settings = get_settings()
        self.model = GroqModel(
            model_name="llama-3.3-70b-versatile",
            api_key=settings.GROQ_API_KEY
        )
        self.agent = Agent(
            model=self.model,
            system_prompt="You are a helpful assistant."
        )
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request."""
        try:
            response = await self.agent.run(request.content)
            return ChatResponse(content=response.data)
        except Exception as e:
            logfire.error("Failed to process message", error=str(e))
            return ChatResponse(content="", error=str(e)) 