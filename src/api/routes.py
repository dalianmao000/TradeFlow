"""API路由定义"""
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from ..agents import (
    CentralAgent,
    PricePredictionAgent,
    CustomerRecommendAgent,
    ProductionSalesAgent,
    SupplyChainAgent,
    RiskControlAgent
)
from ..core.state import AgentStateManager

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化Agent
central_agent = CentralAgent()
price_agent = PricePredictionAgent()
customer_agent = CustomerRecommendAgent()
production_agent = ProductionSalesAgent()
supply_chain_agent = SupplyChainAgent()
risk_agent = RiskControlAgent()

# 状态管理器
state_manager = AgentStateManager()


# 请求模型
class AgentRequest(BaseModel):
    """Agent请求"""
    query: str = Field(..., description="用户查询")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文")
    agent_id: str = Field(..., description="Agent ID")


class PricePredictionRequest(BaseModel):
    """价格预测请求"""
    product: str = Field(..., description="产品")
    region: str = Field(default="华东", description="地区")
    horizon_days: int = Field(default=7, description="预测天数")


class CustomerRecommendRequest(BaseModel):
    """客户推荐请求"""
    product: str = Field(..., description="产品")
    top_n: int = Field(default=10, description="推荐数量")


class ProductionOptimizeRequest(BaseModel):
    """产销优化请求"""
    orders: list = Field(default_factory=list, description="订单列表")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="约束条件")


class RiskMonitorRequest(BaseModel):
    """风控监测请求"""
    monitor_type: str = Field(default="all", description="监测类型: market/credit/contract/all")


# 响应模型
class AgentResponse(BaseModel):
    """Agent响应"""
    success: bool
    data: Dict[str, Any]
    reasoning: str
    confidence: float
    requires_human_review: bool


# 路由定义
@router.post("/agent/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """执行Agent（通过中枢路由）"""
    try:
        # 中枢Agent解析意图并路由
        result = await central_agent.execute({
            "query": request.query,
            "context": request.context
        })

        return AgentResponse(
            success=result.status == "success",
            data=result.data,
            reasoning=result.reasoning,
            confidence=result.confidence,
            requires_human_review=result.requires_human_review
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/price_prediction", response_model=AgentResponse)
async def price_prediction(request: PricePredictionRequest):
    """价格预测"""
    try:
        result = await price_agent.execute({
            "product": request.product,
            "region": request.region,
            "horizon_days": request.horizon_days
        })

        return AgentResponse(
            success=result.status == "success",
            data=result.data,
            reasoning=result.reasoning,
            confidence=result.confidence,
            requires_human_review=result.requires_human_review
        )

    except Exception as e:
        logger.error(f"Price prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/customer_recommend", response_model=AgentResponse)
async def customer_recommend(request: CustomerRecommendRequest):
    """客户推荐"""
    try:
        result = await customer_agent.execute({
            "product": request.product,
            "top_n": request.top_n
        })

        return AgentResponse(
            success=result.status == "success",
            data=result.data,
            reasoning=result.reasoning,
            confidence=result.confidence,
            requires_human_review=result.requires_human_review
        )

    except Exception as e:
        logger.error(f"Customer recommend failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/production_optimize", response_model=AgentResponse)
async def production_optimize(request: ProductionOptimizeRequest):
    """产销协同优化"""
    try:
        result = await production_agent.execute({
            "orders": request.orders,
            "constraints": request.constraints
        })

        return AgentResponse(
            success=result.status == "success",
            data=result.data,
            reasoning=result.reasoning,
            confidence=result.confidence,
            requires_human_review=result.requires_human_review
        )

    except Exception as e:
        logger.error(f"Production optimize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/supply_chain_schedule", response_model=AgentResponse)
async def supply_chain_schedule():
    """供应链调度"""
    try:
        result = await supply_chain_agent.execute({})

        return AgentResponse(
            success=result.status == "success",
            data=result.data,
            reasoning=result.reasoning,
            confidence=result.confidence,
            requires_human_review=result.requires_human_review
        )

    except Exception as e:
        logger.error(f"Supply chain schedule failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/risk_monitor", response_model=AgentResponse)
async def risk_monitor(request: RiskMonitorRequest):
    """风控预警"""
    try:
        result = await risk_agent.execute({
            "monitor_type": request.monitor_type
        })

        return AgentResponse(
            success=result.status == "success",
            data=result.data,
            reasoning=result.reasoning,
            confidence=result.confidence,
            requires_human_review=result.requires_human_review
        )

    except Exception as e:
        logger.error(f"Risk monitor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/health")
async def agent_health():
    """Agent健康检查"""
    return {
        "agents": {
            "central": "healthy",
            "price_prediction": "healthy",
            "customer_recommend": "healthy",
            "production_sales": "healthy",
            "supply_chain": "healthy",
            "risk_control": "healthy"
        }
    }