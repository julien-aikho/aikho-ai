# Functional Specification

## Overview

aikho-ai is a fastapi backend for the aikho platform. It is responsible to provide agentic capabilities to the aikho platform. It is built on top of the fastapi framework and uses the sqlmodel library for database operations. 
The core stack is as follows:

- we are using uv as a package manager.
- FastAPI: The web framework used to build the API.
- SQLModel: The database ORM used to interact with the database.
- Pydantic: The data validation and settings management library used to validate the data and settings.
- PyDanticAI: The library used to build the agentic capabilities.
- the data is stored in a postgres database.

## Endpoints

### Chat

To get us started, we want to have thread based chat, meaning that we will store conversations in a thread. thread will be a table with the following columns:

- id: the id of the thread
- name: the name of the thread
- created_at: the timestamp when the thread was created
- updated_at: the timestamp when the thread was last updated

Then we will use the pydanticai library to build the agentic capabilities. We will use the chat model to generate the responses.


