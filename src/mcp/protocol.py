"""JSON-RPC 2.0 协议处理"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass
import json


@dataclass
class MCPRequest:
    """MCP请求"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None


@dataclass
class MCPResponse:
    """MCP响应"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        response = {"jsonrpc": self.jsonrpc}
        if self.result is not None:
            response["result"] = self.result
        if self.error is not None:
            response["error"] = self.error
        if self.id is not None:
            response["id"] = self.id
        return response


class JSONRPCProtocol:
    """JSON-RPC 2.0 协议处理器"""

    # 错误码定义
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    TIMEOUT = -32000
    SERVICE_UNAVAILABLE = -32001
    RATE_LIMITED = -32002

    def __init__(self):
        self.error_messages = {
            self.PARSE_ERROR: "Parse error - Invalid JSON",
            self.INVALID_REQUEST: "Invalid request",
            self.METHOD_NOT_FOUND: "Method not found",
            self.INVALID_PARAMS: "Invalid params",
            self.INTERNAL_ERROR: "Internal error",
            self.TIMEOUT: "Request timeout",
            self.SERVICE_UNAVAILABLE: "Service unavailable",
            self.RATE_LIMITED: "Rate limited",
        }

    def parse_request(self, raw_json: str) -> MCPRequest:
        """解析请求"""
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON")

        if not isinstance(data, dict):
            raise ValueError("Request must be object")

        if data.get("jsonrpc") != "2.0":
            raise ValueError("Invalid JSON-RPC version")

        return MCPRequest(
            method=data.get("method", ""),
            params=data.get("params"),
            id=data.get("id")
        )

    def create_response(
        self,
        result: Any,
        request_id: Optional[Union[str, int]] = None
    ) -> MCPResponse:
        """创建成功响应"""
        return MCPResponse(
            result=result,
            id=request_id
        )

    def create_error_response(
        self,
        code: int,
        message: Optional[str] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> MCPResponse:
        """创建错误响应"""
        return MCPResponse(
            error={
                "code": code,
                "message": message or self.error_messages.get(code, "Unknown error")
            },
            id=request_id
        )

    def validate_params(self, params: Dict[str, Any], schema: Dict[str, type]) -> bool:
        """验证参数"""
        for key, expected_type in schema.items():
            if key not in params:
                return False
            if not isinstance(params[key], expected_type):
                return False
        return True