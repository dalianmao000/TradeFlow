"""工具注册与调用"""
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    timeout_ms: int = 30000


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._middleware: List[Callable] = []

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        timeout_ms: int = 30000
    ) -> None:
        """注册工具"""
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            timeout_ms=timeout_ms
        )
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self._tools.keys())

    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """执行工具"""
        tool = self.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # 执行中间件
        for mw in self._middleware:
            parameters = mw(tool_name, parameters)

        # 执行工具
        try:
            result = await tool.handler(parameters)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}, error: {e}")
            raise

    def add_middleware(self, middleware: Callable) -> None:
        """添加中间件"""
        self._middleware.append(middleware)


# 全局工具注册表
_global_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """获取全局注册表"""
    return _global_registry


def register_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    timeout_ms: int = 30000
):
    """装饰器：注册工具"""
    def decorator(func: Callable):
        _global_registry.register(
            name=name,
            description=description,
            parameters=parameters,
            handler=func,
            timeout_ms=timeout_ms
        )
        return func
    return decorator