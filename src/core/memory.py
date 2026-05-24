"""Agent记忆机制"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MemoryItem:
    """记忆条目"""
    key: str
    value: Any
    timestamp: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentMemory:
    """Agent记忆 - 短期记忆、长期记忆、业务记忆"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._short_term: Dict[str, MemoryItem] = {}
        self._long_term: Dict[str, MemoryItem] = {}
        self._business_state: Dict[str, Any] = {}
        self.max_short_term_items = 50

    def store_short_term(self, key: str, value: Any) -> None:
        """存储短期记忆"""
        item = MemoryItem(
            key=key,
            value=value,
            timestamp=datetime.now()
        )
        self._short_term[key] = item

        # 限制短期记忆大小
        if len(self._short_term) > self.max_short_term_items:
            oldest_key = min(
                self._short_term.keys(),
                key=lambda k: self._short_term[k].timestamp
            )
            del self._short_term[oldest_key]

    def get_short_term(self, key: str) -> Optional[Any]:
        """获取短期记忆"""
        item = self._short_term.get(key)
        if item:
            return item.value
        return None

    def store_long_term(self, key: str, value: Any, ttl_days: int = 30) -> None:
        """存储长期记忆"""
        from datetime import timedelta
        item = MemoryItem(
            key=key,
            value=value,
            timestamp=datetime.now(),
            expires_at=datetime.now() + timedelta(days=ttl_days)
        )
        self._long_term[key] = item

    def get_long_term(self, key: str) -> Optional[Any]:
        """获取长期记忆"""
        item = self._long_term.get(key)
        if item:
            # 检查是否过期
            if item.expires_at and datetime.now() > item.expires_at:
                del self._long_term[key]
                return None
            return item.value
        return None

    def update_business_state(self, key: str, value: Any) -> None:
        """更新业务状态"""
        self._business_state[key] = value

    def get_business_state(self, key: str) -> Optional[Any]:
        """获取业务状态"""
        return self._business_state.get(key)

    def get_context_window(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取上下文窗口（最近的短期记忆）"""
        items = sorted(
            self._short_term.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]

        return [
            {"key": item.key, "value": item.value, "timestamp": item.timestamp.isoformat()}
            for item in items
        ]

    def clear_short_term(self) -> None:
        """清除短期记忆"""
        self._short_term.clear()

    def to_dict(self) -> Dict[str, Any]:
        """序列化记忆"""
        return {
            "agent_id": self.agent_id,
            "short_term": {
                k: {"value": v.value, "timestamp": v.timestamp.isoformat()}
                for k, v in self._short_term.items()
            },
            "business_state": self._business_state
        }