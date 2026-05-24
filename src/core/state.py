"""LangGraph状态管理"""
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent状态"""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(TypedDict):
    """LangGraph使用的Agent状态"""
    messages: List[Dict[str, Any]]
    current_agent: str
    agent_results: Dict[str, Any]
    confidence: float
    requires_review: bool
    context: Dict[str, Any]


@dataclass
class AgentSnapshot:
    """Agent状态快照"""
    agent_id: str
    status: AgentStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    timestamp: datetime
    execution_time_ms: int = 0


class AgentStateManager:
    """Agent状态管理器"""

    def __init__(self):
        self.snapshots: Dict[str, List[AgentSnapshot]] = {}
        self.current_state: Dict[str, AgentState] = {}

    def create_state(
        self,
        agent_id: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> AgentState:
        """创建新状态"""
        state: AgentState = {
            "messages": [],
            "current_agent": agent_id,
            "agent_results": {},
            "confidence": 1.0,
            "requires_review": False,
            "context": initial_context or {}
        }
        self.current_state[agent_id] = state
        return state

    def update_state(
        self,
        agent_id: str,
        updates: Dict[str, Any]
    ) -> AgentState:
        """更新状态"""
        if agent_id not in self.current_state:
            self.create_state(agent_id)

        for key, value in updates.items():
            self.current_state[agent_id][key] = value

        return self.current_state[agent_id]

    def add_message(
        self,
        agent_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """添加消息"""
        if agent_id not in self.current_state:
            self.create_state(agent_id)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.current_state[agent_id]["messages"].append(message)

    def save_snapshot(self, snapshot: AgentSnapshot) -> None:
        """保存快照"""
        if snapshot.agent_id not in self.snapshots:
            self.snapshots[snapshot.agent_id] = []

        self.snapshots[snapshot.agent_id].append(snapshot)

        # 只保留最近100个快照
        if len(self.snapshots[snapshot.agent_id]) > 100:
            self.snapshots[snapshot.agent_id] = self.snapshots[snapshot.agent_id][-100:]

    def get_latest_snapshot(self, agent_id: str) -> Optional[AgentSnapshot]:
        """获取最新快照"""
        snapshots = self.snapshots.get(agent_id, [])
        return snapshots[-1] if snapshots else None

    def get_state(self, agent_id: str) -> Optional[AgentState]:
        """获取当前状态"""
        return self.current_state.get(agent_id)

    def clear_state(self, agent_id: str) -> None:
        """清除状态"""
        if agent_id in self.current_state:
            del self.current_state[agent_id]