"""Main application module."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logfire
from pathlib import Path

# Import models first so SQLModel knows what tables to create
from app.models.thread import Thread
from app.models.message import Message, MessagePart

from app.routers import chat
from app.db.core import create_db_and_tables
from app.agents.registry import AgentRegistry

app = FastAPI()

# Configure logging
logfire.configure()
logfire.instrument_fastapi(app)

# Get the template directory
templates_dir = Path(__file__).parent / "templates"

@app.on_event("startup")
async def on_startup():
    """Initialize application dependencies."""
    try:
        # Initialize database
        create_db_and_tables()
        logfire.info("Database initialized")
        
        # Load and register agents
        AgentRegistry.load_from_config()
        logfire.info("Agents loaded")
        
        # Log available agents
        agents = AgentRegistry.list()
        logfire.info("Available agents", count=len(agents), agents=[a["id"] for a in agents])
        
    except Exception as e:
        logfire.error("Failed to initialize application", error=str(e))
        raise

app.include_router(chat.router)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the chat interface."""
    return (templates_dir / "index.html").read_text()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

