from typing import Any, Generator
from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends
from app.config import Settings
from sqlalchemy import text

settings = Settings()
SCHEMA_NAME = "aikho_ai"

def get_engine(db_url: str = settings.DATABASE_URL) -> Any:
    engine = create_engine(db_url, echo=False)
    return engine

def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """Call this at startup to create all tables"""
    engine = get_engine()
    
    # Create schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}'))
        conn.commit()
    
    # Set schema for all models
    SQLModel.metadata.schema = SCHEMA_NAME
    
    # Create all tables in the schema
    SQLModel.metadata.create_all(engine)

