"""Full chat agent implementation with tools."""

import logfire
import random
from typing import Sequence
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.result import RunResult
from pydantic_ai.models.groq import GroqModel
from app.agents.chat import ChatAgent, ChatRequest, ChatResponse, AgentDeps
from app.config import get_settings

def roll_dice(dice_type: str) -> str:
    """Use every time the user asks to roll a dice, can be d6, d10, d20. you must specify the type of dice"""
    if dice_type == 'd6':
        x:int = random.randint(1, 6)
    elif dice_type == 'd10':
        x:int = random.randint(1, 10)
    elif dice_type == 'd20':
        x:int = random.randint(1, 20)
    return f'You rolled a {x}'

class FullAgent(ChatAgent):
    """A chat agent with full capabilities."""
    
    def __init__(self):
        settings = get_settings()
        self.model = GroqModel(
            model_name="llama-3.3-70b-versatile",
            api_key=settings.GROQ_API_KEY
        )
        self.agent = Agent(
            model=self.model,
            system_prompt="You are a helpful assistant. Never roll a dice without calling the function. Your name is Aikho.",
            tools=[roll_dice],
        )
    
    async def _process_chat(self, request: ChatRequest, deps: AgentDeps, message_history: list[ModelMessage]) -> RunResult:
        """Process a chat request."""
        try:
            return await self.agent.run(request.content, message_history=message_history)
        except Exception as e:
            logfire.error("Failed to process message", error=str(e))
            raise


