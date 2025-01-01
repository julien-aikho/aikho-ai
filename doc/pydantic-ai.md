# PydanticAI Framework

PydanticAI is a Python Agent Framework designed to make it less painful to build production-grade applications with Generative AI. Built by the Pydantic team, it brings the "FastAPI feeling" to GenAI app development.

## Key Features

- **Model-agnostic**: Supports OpenAI, Anthropic, Gemini, Ollama, Groq, and Mistral
- **Type-safe**: Integrates well with static type checkers like `mypy` and `pyright`
- **Python-centric Design**: Leverages Python's familiar control flow and agent composition
- **Structured Responses**: Uses Pydantic to validate and structure model outputs
- **Dependency Injection**: Optional system for providing data and services
- **Streamed Responses**: Ability to stream LLM outputs with immediate validation

## Installation

Basic installation:
```bash
pip install pydantic-ai
```

With Logfire integration:
```bash
pip install 'pydantic-ai[logfire]'
```

Slim installation (for specific models):
```bash
pip install 'pydantic-ai-slim[openai]'  # Example with OpenAI only
```

Requirements:
- Python 3.9+

## Basic Usage

Here's a simple example:

```python
from pydantic_ai import Agent

agent = Agent(
    'gemini-1.5-flash',
    system_prompt='Be concise, reply with one sentence.',
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.data)
# Output: The first known use of "hello, world" was in a 1974 textbook about the C programming language.
```

## Tools and Dependency Injection

PydanticAI provides a powerful system for tools and dependency injection that allows models to retrieve extra information and make agent behavior more deterministic.

### Function Tools

There are three ways to register tools with an agent:

1. Using `@agent.tool` decorator (for tools needing access to agent context)
2. Using `@agent.tool_plain` decorator (for tools not needing context)
3. Via the `tools` keyword argument to `Agent`

Here's a simple example:

```python
import random
from pydantic_ai import Agent, RunContext

agent = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    system_prompt=(
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner. "
        "Use the player's name in the response."
    ),
)

@agent.tool_plain
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))

@agent.tool
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps

# Use the agent
result = agent.run_sync('My guess is 4', deps='Anne')
print(result.data)
# Output: Congratulations Anne, you guessed correctly! You're a winner!
```

### Tool Registration via Constructor

You can also register tools when creating the agent:

```python
# Using function list
agent_a = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    tools=[roll_die, get_player_name],
)

# Using Tool instances for more control
from pydantic_ai import Tool

agent_b = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    tools=[
        Tool(roll_die, takes_ctx=False),
        Tool(get_player_name, takes_ctx=True),
    ],
)
```

### Tool Schema and Documentation

PydanticAI automatically extracts function parameters and docstrings to build the schema for tool calls. It supports:
- Parameter type hints
- Docstring extraction (Google, NumPy, and Sphinx styles)
- Automatic schema generation for the model

## Supported Models

PydanticAI supports multiple model providers out of the box:

### OpenAI

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Using model by name
agent = Agent('openai:gpt-4o')

# Or initialize directly
model = OpenAIModel('gpt-4o', api_key='your-api-key')
agent = Agent(model)
```

Configuration:
```bash
export OPENAI_API_KEY='your-api-key'
```

### Anthropic

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

# Using model by name
agent = Agent('claude-3-5-sonnet-latest')

# Or initialize directly
model = AnthropicModel('claude-3-5-sonnet-latest', api_key='your-api-key')
agent = Agent(model)
```

Configuration:
```bash
export ANTHROPIC_API_KEY='your-api-key'
```

### Gemini

Available through two APIs:

1. Generative Language API (for prototyping):
```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

agent = Agent('gemini-1.5-flash')
# or
model = GeminiModel('gemini-1.5-flash', api_key='your-api-key')
agent = Agent(model)
```

Configuration:
```bash
export GEMINI_API_KEY='your-api-key'
```

2. VertexAI API (recommended for production):
```python
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel('gemini-1.5-flash')
agent = Agent(model)
```

### Other Supported Models

- **Ollama**: For running models locally
- **Groq**: Cloud API for fast inference
- **Mistral**: Direct API access to Mistral models

### Custom Models

PydanticAI allows implementing custom model support by extending the base model classes.

## Structured Responses and Validation

PydanticAI provides powerful features for handling structured responses and validation using Pydantic models.

### Basic Structured Results

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent('gemini-1.5-flash', result_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.data)  # Output: city='London' country='United Kingdom'
```

### Union Types for Multiple Response Types

```python
from typing import Union
from pydantic import BaseModel

class Box(BaseModel):
    width: int
    height: int
    depth: int
    units: str

agent: Agent[None, Union[Box, str]] = Agent(
    'openai:gpt-4o-mini',
    result_type=Union[Box, str],  # type: ignore
    system_prompt="Extract box dimensions, if can't extract all data, ask user to try again."
)

result = agent.run_sync('The box is 10x20x30')
print(result.data)  # Output: "Please provide the units for the dimensions"

result = agent.run_sync('The box is 10x20x30 cm')
print(result.data)  # Output: width=10 height=20 depth=30 units='cm'
```

### Result Validators

You can add custom validation functions using the `@agent.result_validator` decorator:

```python
from typing import Union
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ModelRetry

class Success(BaseModel):
    sql_query: str

class InvalidRequest(BaseModel):
    error_message: str

Response = Union[Success, InvalidRequest]

agent: Agent[DatabaseConn, Response] = Agent(
    'gemini-1.5-flash',
    result_type=Response,  # type: ignore
    deps_type=DatabaseConn,
    system_prompt='Generate PostgreSQL flavored SQL queries based on user input.',
)

@agent.result_validator
async def validate_result(ctx: RunContext[DatabaseConn], result: Response) -> Response:
    if isinstance(result, InvalidRequest):
        return result
    try:
        await ctx.deps.execute(f'EXPLAIN {result.sql_query}')
    except QueryError as e:
        raise ModelRetry(f'Invalid query: {e}') from e
    return result

### Streamed Responses

PydanticAI supports streaming responses for both text and structured data:

```python
# Text streaming
async with agent.run_stream('Where does "hello world" come from?') as result:
    async for message in result.stream():
        print(message)  # Prints incrementally complete responses

# Delta streaming (only changes)
async with agent.run_stream('Where does "hello world" come from?') as result:
    async for message in result.stream_text(delta=True):
        print(message)  # Prints only the new parts of the response
```

For structured data, you can use TypedDict for partial validation during streaming:

```python
from typing_extensions import TypedDict
from datetime import date

class UserProfile(TypedDict, total=False):
    name: str
    dob: date
    bio: str

agent = Agent(
    'openai:gpt-4o',
    result_type=UserProfile,
    system_prompt='Extract a user profile from the input'
)

# Stream the structured response as it's built
async with agent.run_stream('...') as result:
    async for profile in result.stream():
        print(profile)  # Shows the profile as it's being built
```

[More sections to be added...]

