"""应用配置"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from dataclasses import dataclass, field
import os
import json


@dataclass
class AgentConfig:
    """Agent配置"""
    agent_id: str
    name: str
    enabled: bool = True
    tools: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    timeout_ms: int = 30000


@dataclass
class MCPServerConfig:
    """MCP服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    services: List[str] = field(default_factory=list)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    database: str
    username: str
    password: str

    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class AppConfig:
    """应用配置"""
    app_name: str = "tradflow-ai-agent"
    environment: str = "dev"
    debug: bool = True

    # Agent配置
    agents: List[AgentConfig] = field(default_factory=list)

    # MCP服务配置
    mcp_servers: List[MCPServerConfig] = field(default_factory=list)

    # 数据库配置
    database: Optional[DatabaseConfig] = None

    # LLM配置
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None

    # 安全配置
    auth_enabled: bool = True
    rate_limit_per_minute: int = 60


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """加载配置"""
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "configs/app.yaml")

    if not os.path.exists(config_path):
        # 返回默认配置
        return AppConfig()

    with open(config_path, "r") as f:
        data = json.load(f)

    # 解析Agent配置
    agents = [
        AgentConfig(**a) for a in data.get("agents", [])
    ]

    # 解析MCP服务配置
    mcp_servers = [
        MCPServerConfig(**m) for m in data.get("mcp_servers", [])
    ]

    # 解析数据库配置
    db_config = None
    if "database" in data:
        db_config = DatabaseConfig(**data["database"])

    return AppConfig(
        app_name=data.get("app_name", "tradflow-ai-agent"),
        environment=data.get("environment", "dev"),
        debug=data.get("debug", True),
        agents=agents,
        mcp_servers=mcp_servers,
        database=db_config,
        llm_provider=data.get("llm_provider", "openai"),
        llm_model=data.get("llm_model", "gpt-4"),
        llm_api_key=data.get("llm_api_key"),
        llm_base_url=data.get("llm_base_url"),
        auth_enabled=data.get("auth_enabled", True),
        rate_limit_per_minute=data.get("rate_limit_per_minute", 60)
    )


# 默认配置
DEFAULT_CONFIG = AppConfig(
    agents=[
        AgentConfig(agent_id="central", name="中枢Agent", tools=["route"]),
        AgentConfig(agent_id="price_prediction", name="价格预测Agent", tools=["ml.predict"]),
        AgentConfig(agent_id="customer_recommend", name="客户推荐Agent", tools=["crm.query"]),
        AgentConfig(agent_id="production_sales", name="产销Agent", tools=["opt.production"]),
        AgentConfig(agent_id="supply_chain", name="供应链Agent", tools=["opt.route"]),
        AgentConfig(agent_id="risk_control", name="风控Agent", tools=["risk.analyze"]),
    ],
    mcp_servers=[
        MCPServerConfig(host="0.0.0.0", port=8000, services=["rag", "ml"]),
        MCPServerConfig(host="0.0.0.0", port=8001, services=["opt", "kg"]),
    ]
)