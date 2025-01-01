"""Chat endpoints."""

from fastapi import APIRouter
import logfire
from app.agents.registry import AgentRegistry
from app.agents.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat")

@router.post("/message")
async def send_message(request: ChatRequest) -> dict:
    """Send a message to an agent."""
    try:
        agent = AgentRegistry.get(request.agent_id)
        response = await agent.chat(request)
        return {"response": response}
    except Exception as e:
        logfire.error("Failed to process message", error=str(e))
        return {"response": ChatResponse(
            content="Sorry, I encountered an error.",
            error=str(e)
        )}

@router.get("/agents")
async def list_agents() -> list[dict]:
    """List available agents."""
    return AgentRegistry.list()
