"""MCP Server 主入口"""
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .protocol import JSONRPCProtocol, MCPRequest, MCPResponse
from .services.rag_service import RAGService
from .services.ml_service import MLService
from .services.opt_service import OptimizationService
from .services.kg_service import KnowledgeGraphService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: int
    dependencies: Dict[str, str]


class MCPApp:
    """MCP Server应用"""

    def __init__(self, port: int = 8000):
        self.port = port
        self.app = FastAPI(title="MCP Server", version="1.0.0")
        self.protocol = JSONRPCProtocol()

        # 初始化服务
        self.services = {
            "rag": RAGService(),
            "ml": MLService(),
            "opt": OptimizationService(),
            "kg": KnowledgeGraphService(),
        }

        self._setup_routes()
        self.start_time = None

    def _setup_routes(self):
        """设置路由"""

        @self.app.get("/health", response_model=HealthResponse)
        async def health():
            import time
            return HealthResponse(
                status="healthy",
                version="1.0.0",
                uptime_seconds=int(time.time() - (self.start_time or time.time())),
                dependencies={
                    "vector_db": "connected",
                    "cache": "connected"
                }
            )

        @self.app.post("/v1/rag/search")
        async def rag_search(request: dict):
            """RAG检索"""
            mcp_request = MCPRequest(method="rag.search", params=request)
            result = await self.services["rag"].search(mcp_request.params)
            return {"jsonrpc": "2.0", "result": result, "id": mcp_request.id}

        @self.app.post("/v1/ml/predict_price")
        async def ml_predict_price(request: dict):
            """价格预测"""
            mcp_request = MCPRequest(method="ml.predict_price", params=request)
            result = await self.services["ml"].predict_price(mcp_request.params)
            return {"jsonrpc": "2.0", "result": result, "id": mcp_request.id}

        @self.app.post("/v1/opt/production_optimize")
        async def opt_production(request: dict):
            """产销优化"""
            mcp_request = MCPRequest(method="opt.production_optimize", params=request)
            result = await self.services["opt"].production_optimize(mcp_request.params)
            return {"jsonrpc": "2.0", "result": result, "id": mcp_request.id}

        @self.app.post("/v1/kg/query")
        async def kg_query(request: dict):
            """知识图谱查询"""
            mcp_request = MCPRequest(method="kg.query", params=request)
            result = await self.services["kg"].query(mcp_request.params)
            return {"jsonrpc": "2.0", "result": result, "id": mcp_request.id}

    def run(self):
        """启动服务"""
        import time
        self.start_time = time.time()
        logger.info(f"Starting MCP Server on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


if __name__ == "__main__":
    server = MCPApp(port=8000)
    server.run()