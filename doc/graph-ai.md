# This is the conceptual and technical doc for graph-ai, the fundamental structure underlying aikho-ai

# This is the conceptual and technical doc for graph-ai, the fundamental structure underlying aikho-ai

## Overview

graph-ai is a framework that provides agentic capabilities through API-served workflows, built on top of PydanticAI's agent framework. It enables both interactive and automated AI-powered workflows through a graph-based architecture.

## Core Concepts

### Agentic Workflows

An agentic workflow in graph-ai is represented as:
- A Directed Acyclic Graph (DAG) with underlying state
- Nodes can be either:
  - Standard functions
  - LLM-powered operations (via PydanticAI agents)
- Each workflow maintains its state throughout execution

### Use Cases

#### 1. Chat Mode
- Interactive communication with users
- Leverages PydanticAI's features:
  - Structured responses
  - Real-time streaming
  - Type-safe interactions
  - Model-agnostic support

#### 2. Execution Mode
Automated task execution following a typical pattern:
1. Data Ingestion: Pull data from source systems
2. State Construction: Build the graph state
3. Processing: Execute the graph workflow
4. Output: Transform and deliver results based on the final state

## Technical Implementation

[TODO: Add details about:
- Graph state management
- Node execution patterns
- Integration with PydanticAI
- API design
- State persistence
- Error handling]