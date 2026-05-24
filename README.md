# TradeFlow AI Agent

Multi-Agent AI System for Chemical Trading - intelligent automation with human-in-the-loop governance

## Project Structure

```
tradflow-ai-agent/
├── src/
│   ├── agents/          # 6 agents: central + 5 vertical business agents
│   ├── mcp/             # MCP Server implementation
│   │   └── services/    # RAG/ML/Optimization/KnowledgeGraph services
│   ├── core/            # Core components (config/state/tools/memory)
│   └── api/             # FastAPI entry point
├── docker/              # Docker configuration
├── k8s/                 # Kubernetes deployment configs
├── configs/             # Agent and service configs
├── tests/               # Tests
└── scripts/             # Scripts
```

## Quick Start

### 1. Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start API service
python -m src.api.main

# Start MCP service
python -m src.mcp.server
```

### 2. Docker

```bash
# Build image
docker build -f docker/Dockerfile.agent -t tradflow-ai-agent:latest .

# Run container
docker run -p 8000:8000 tradflow-ai-agent:latest
```

### 3. Kubernetes

```bash
# Apply base configs
kubectl apply -f k8s/base/

# Apply dev environment
kubectl apply -f k8s/overlays/dev/
```

## API Endpoints

| Endpoint | Method | Description |
|:---|:---|:---|
| `/api/v1/agent/execute` | POST | Central agent routing |
| `/api/v1/agent/price_prediction` | POST | Market price prediction |
| `/api/v1/agent/customer_recommend` | POST | Customer recommendation |
| `/api/v1/agent/production_optimize` | POST | Production-sales coordination |
| `/api/v1/agent/supply_chain_schedule` | POST | Supply chain scheduling |
| `/api/v1/agent/risk_monitor` | POST | Risk monitoring |
| `/health` | GET | Health check |

## Agent List

| Agent | Function |
|:---|:---|
| `central` | Central Agent - intent recognition, task routing |
| `price_prediction` | Market price forecasting |
| `customer_recommend` | Intelligent customer recommendation |
| `production_sales` | Production-sales coordination |
| `supply_chain` | Supply chain scheduling |
| `risk_control` | Risk monitoring and alerts |

## Architecture

- **5-layer architecture**: Interaction → Orchestration → Agent Cluster → Tools → Data
- **Multi-Agent collaboration**: Parallel execution with result aggregation
- **Human-in-the-loop**: Configurable approval workflows for critical decisions
- **Enterprise-ready**: RBAC, audit logs, data classification

## Tech Stack

- Python 3.11+
- FastAPI + LangGraph
- PostgreSQL + Milvus + NebulaGraph
- Docker + Kubernetes
- Prometheus + Grafana

## License

MIT