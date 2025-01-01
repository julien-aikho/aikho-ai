"""Chat agent interface and implementations."""

from typing import Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel
import logfire
from sqlmodel import Session, select
from pydantic_ai.messages import (
    ModelMessage, ModelRequest, ModelResponse,
    ModelRequestPart, ModelResponsePart,
    UserPromptPart, TextPart, ToolCallPart, ToolReturnPart,
    ArgsDict
)
from pydantic_ai.result import RunResult
from app.models.message import Message, MessagePart, MessageKind
from app.models.thread import Thread
from app.db.core import get_engine

@dataclass
class AgentDeps:
    """Dependencies for chat agents."""
    session: Session

class ChatResponse(BaseModel):
    """Response from a chat agent."""
    content: str
    error: Optional[str] = None
    parts: list[dict[str, Any]] = []

class ChatRequest(BaseModel):
    """Request to a chat agent."""
    content: str
    agent_id: str
    user_id: str = "default"

class ChatAgent:
    """Base interface for chat agents."""
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and return a response."""
        engine = get_engine()
        with Session(engine) as session:
            deps = AgentDeps(session=session)
            
            # Get or create thread
            statement = select(Thread).where(
                Thread.user_id == request.user_id,
                Thread.persona_id == request.agent_id
            )
            thread = session.exec(statement).first()
            
            if not thread:
                thread = Thread(
                    user_id=request.user_id,
                    persona_id=request.agent_id,
                    name=f"Chat with {request.agent_id}"
                )
                session.add(thread)
                session.flush()  # Get thread.id
            
            # Load previous messages
            statement = select(Message).where(
                Message.thread_id == thread.id
            ).order_by("timestamp")
            thread_messages = session.exec(statement).all()
            
            # Convert all messages to ModelMessage format without filtering parts
            message_history = []
            
            # Add system prompt if it exists
            statement = select(Message).join(MessagePart).where(
                Message.thread_id == thread.id,
                MessagePart.part_kind == "system-prompt"
            )
            system_message = session.exec(statement).first()
            if system_message:
                data = system_message.to_model_message()
                logfire.debug("Adding system prompt to history", message_data=data)
                message_history.append(ModelRequest(parts=[
                    UserPromptPart(content=data["parts"][0]["content"])
                ]))
            
            # Add rest of message history
            for msg in thread_messages:
                if msg.id == system_message.id if system_message else None:
                    continue  # Skip system message as it's already added
                data = msg.to_model_message()
                logfire.debug("Converting message to model format", message_data=data)
                if data["kind"] == "request":
                    parts = []
                    for part in data["parts"]:
                        logfire.debug("Processing request part", part=part)
                        if part["part_kind"] == "user-prompt":
                            parts.append(UserPromptPart(content=part["content"]))
                        elif part["part_kind"] == "tool-return":
                            parts.append(ToolReturnPart(
                                content=part["content"],
                                tool_name=part["tool_name"],
                                tool_call_id=part["tool_call_id"]
                            ))
                    message_history.append(ModelRequest(parts=parts))
                else:
                    parts = []
                    for part in data["parts"]:
                        logfire.debug("Processing response part", part=part)
                        if part["part_kind"] == "text":
                            parts.append(TextPart(content=part["content"]))
                        elif part["part_kind"] == "assistant-message":
                            parts.append(TextPart(content=part["content"]))
                        elif part["part_kind"] == "tool-call":
                            args_dict = {"args_json": part["args_json"]} if part["args_json"] else {}
                            parts.append(ToolCallPart(
                                tool_name=part["tool_name"],
                                tool_call_id=part["tool_call_id"],
                                args=ArgsDict(args_dict=args_dict)
                            ))
                    message_history.append(ModelResponse(parts=parts))
            
            try:
                # Process chat with history
                result = await self._process_chat(request, deps, message_history)
                logfire.debug("Got result from _process_chat", result=result)
                
                # Get new messages from the result
                new_messages = result.new_messages()
                logfire.debug("New messages from result", messages=new_messages)
                
                # Save all new messages
                for msg in new_messages:
                    msg_kind = MessageKind.REQUEST if msg.kind == "request" else MessageKind.RESPONSE
                    msg_data = Message(
                        thread_id=thread.id,
                        kind=msg_kind
                    )
                    session.add(msg_data)
                    session.flush()
                    
                    for part in msg.parts:
                        part_data = MessagePart(
                            message_id=msg_data.id,
                            part_kind=part.part_kind,
                            content=getattr(part, "content", None),
                            tool_name=getattr(part, "tool_name", None),
                            tool_call_id=getattr(part, "tool_call_id", None),
                            args_json=str(part.args) if isinstance(part, ToolCallPart) and part.args else None
                        )
                        session.add(part_data)
                
                session.commit()
                return ChatResponse(content=result.data)
                
            except Exception as e:
                logfire.error("Failed to process message", error=str(e))
                session.rollback()
                return ChatResponse(content="", error=str(e))
    
    async def _process_chat(self, request: ChatRequest, deps: AgentDeps, message_history: list[ModelMessage]) -> RunResult:
        """Subclasses should implement this to process the chat request."""
        raise NotImplementedError("Chat agents must implement _process_chat()")
    
    