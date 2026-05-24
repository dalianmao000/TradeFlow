# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradeFlow AI Agent is a multi-agent AI system for chemical trading with human-in-the-loop governance. It features a 5-layer architecture: Interaction → Orchestration → Agent Cluster → Tools → Data.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server (port 8000)
python -m src.api.main

# Run MCP server (port 8000)
python -m src.mcp.server

# Docker development
docker-compose -f docker/docker-compose.yml up

# Kubernetes deployment
kubectl apply -f k8s/base/
```

## Architecture

### Agent System (`src/agents/`)
- **BaseAgent** (`base.py`): Abstract base class for all agents. All agents must implement `execute()` and `validate_constraints()` methods.
- **CentralAgent** (`central.py`): Intent recognition and task routing hub. Routes user queries to appropriate specialized agents.
- **Specialized Agents**: `PricePredictionAgent`, `CustomerRecommendAgent`, `ProductionSalesAgent`, `SupplyChainAgent`, `RiskControlAgent`

### Standard Agent Output Format
Every agent returns `AgentOutput` with fields: `agent_id`, `timestamp`, `status`, `confidence`, `data`, `reasoning`, `requires_human_review`.

### MCP Server (`src/mcp/`)
- **JSONRPCProtocol** (`protocol.py`): JSON-RPC 2.0 implementation with error codes -32700 to -32002
- **Services** (`services/`): RAG, ML, Optimization, KnowledgeGraph services

### API Layer (`src/api/`)
- FastAPI application defined in `main.py`
- Routes in `routes.py` - one endpoint per agent
- Agents are instantiated as singletons at module load

### State Management (`src/core/state.py`)
- `AgentState`: TypedDict for LangGraph state with `messages`, `current_agent`, `agent_results`, `confidence`, `requires_review`, `context`
- `AgentStateManager`: Manages agent snapshots and current states

## Key Design Patterns

1. **All agents are async**: Use `async def execute()` for non-blocking operations
2. **HITL (Human-in-the-Loop)**: CentralAgent checks `hitl_rules` to flag requests requiring human review
3. **MCP Protocol**: Agent-to-tool communication uses JSON-RPC 2.0 with standardized error codes
4. **Constraint Validation**: Each agent implements `validate_constraints()` to enforce business rules

## File Naming Conventions

- Python files: lowercase with underscores (`price_prediction.py`)
- Config files: YAML in `configs/` directory
- Agent configs: `agents.yaml`
- MCP service configs: `mcp_services.yaml`

## Status

- API framework: Complete
- Agent implementations: Complete (simulation mode, needs real LLM/DB integration)
- Tests: Placeholder only
- CI/CD: Not configured