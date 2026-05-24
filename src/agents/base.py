"""Agent基类 - 所有Agent的父类"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentOutput:
    """Agent输出标准格式"""
    agent_id: str
    timestamp: datetime
    status: str  # success, partial, failed
    confidence: float
    data: Dict[str, Any]
    reasoning: str
    data_sources: List[str] = field(default_factory=list)
    constraints_satisfied: bool = True
    requires_human_review: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "confidence": self.confidence,
            "data": self.data,
            "reasoning": self.reasoning,
            "data_sources": self.data_sources,
            "constraints_satisfied": self.constraints_satisfied,
            "requires_human_review": self.requires_human_review,
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """Agent基类，定义通用接口"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        tools: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.tools = tools or []
        self.constraints = constraints or []
        self.logger = logging.getLogger(f"agent.{agent_id}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """执行Agent逻辑，返回标准化输出"""
        pass

    @abstractmethod
    async def validate_constraints(self, output: AgentOutput) -> bool:
        """验证业务约束是否满足"""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "agent_id": self.agent_id,
            "status": "healthy",
            "tools": self.tools
        }

    def _create_output(
        self,
        status: str,
        confidence: float,
        data: Dict[str, Any],
        reasoning: str,
        requires_human_review: bool = False
    ) -> AgentOutput:
        """创建标准化的Agent输出"""
        return AgentOutput(
            agent_id=self.agent_id,
            timestamp=datetime.now(),
            status=status,
            confidence=confidence,
            data=data,
            reasoning=reasoning,
            requires_human_review=requires_human_review,
            metadata={
                "execution_time_ms": 0,  # 实际执行时由调用方填充
                "tokens_used": 0,
                "model_version": "v1.0"
            }
        )