"""供应链调度Agent"""
from typing import Any, Dict, List
from .base import BaseAgent, AgentOutput
import asyncio


class SupplyChainAgent(BaseAgent):
    """供应链调度Agent"""

    def __init__(self):
        super().__init__(
            agent_id="supply_chain",
            name="供应链调度Agent",
            role="多节点物流路径规划与动态rerouting",
            tools=[
                "query_tms_orders",
                "query_carrier_quotes",
                "get_realtime_traffic",
                "get_weather_data",
                "run_route_optimizer",
                "check_hazmat_rules",
                "calculate_load_balance",
                "generate_emergency_plan"
            ],
            constraints=[
                "危化品运输规范 → 硬编码规则，不可绕过",
                "调度变更需二级审批流拦截",
                "车辆装载率 < 60% → 触发合并优化",
                "天气/路况异常 → 自动rerouting"
            ]
        )

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """执行供应链调度"""
        self.logger.info("执行供应链调度")

        try:
            # 1. 获取TMS数据
            tms_data = await self._query_tms_data()

            # 2. 获取承运商报价
            carrier_quotes = await self._query_carrier_quotes()

            # 3. 获取实时路况
            traffic = await self._get_realtime_traffic()

            # 4. 获取天气数据
            weather = await self._get_weather_data()

            # 5. 危化品合规校验
            compliance = await self._check_hazmat_rules(tms_data)
            if not compliance["passed"]:
                return self._create_output(
                    status="failed",
                    confidence=0.0,
                    data={"compliance_violations": compliance["violations"]},
                    reasoning=f"危化品合规校验失败: {compliance['violations']}",
                    requires_human_review=True
                )

            # 6. 路径优化
            route_result = await self._run_route_optimizer(
                tms_data, carrier_quotes, traffic, weather
            )

            # 7. 装载优化
            load_balance = await self._calculate_load_balance(route_result)

            reasoning = f"调度完成：{len(route_result['routes'])}条路线，总成本={route_result['total_cost']}元"
            reasoning += f"，平均装载率={load_balance['average_utilization']:.1%}"

            return self._create_output(
                status="success",
                confidence=0.90,
                data={
                    "schedule": route_result,
                    "load_balance": load_balance,
                    "compliance_check": compliance
                },
                reasoning=reasoning,
                requires_human_review=False
            )

        except Exception as e:
            self.logger.error(f"供应链调度失败: {e}")
            return self._create_output(
                status="failed",
                confidence=0.0,
                data={"error": str(e)},
                reasoning=f"调度失败: {str(e)}",
                requires_human_review=True
            )

    async def _query_tms_data(self) -> List[Dict[str, Any]]:
        """查询TMS运输订单"""
        await asyncio.sleep(0.1)
        return [
            {"order_id": "T001", "origin": "泉州", "destination": "上海", "volume": 15, "hazmat": True},
            {"order_id": "T002", "origin": "泉州", "destination": "南京", "volume": 10, "hazmat": False},
        ]

    async def _query_carrier_quotes(self) -> List[Dict[str, Any]]:
        """查询承运商报价"""
        await asyncio.sleep(0.1)
        return [
            {"carrier_id": "C1", "name": "承运商A", "price_per_km": 3.5, "available": True},
            {"carrier_id": "C2", "name": "承运商B", "price_per_km": 3.2, "available": True},
        ]

    async def _get_realtime_traffic(self) -> Dict[str, Any]:
        """获取实时路况"""
        await asyncio.sleep(0.1)
        return {
            "泉州-上海": {"congestion": "moderate", "estimated_delay_min": 15},
            "泉州-南京": {"congestion": "light", "estimated_delay_min": 5}
        }

    async def _get_weather_data(self) -> Dict[str, Any]:
        """获取天气数据"""
        await asyncio.sleep(0.1)
        return {
            "泉州": {"condition": "sunny", "temperature": 28},
            "上海": {"condition": "cloudy", "temperature": 22},
            "南京": {"condition": "rainy", "temperature": 18}
        }

    async def _check_hazmat_rules(self, tms_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """危化品合规校验"""
        violations = []

        for order in tms_data:
            if order.get("hazmat"):
                # 模拟危化品规则检查
                if order["volume"] > 20:
                    violations.append(f"订单{order['order_id']}违反危化品装载上限")

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    async def _run_route_optimizer(
        self,
        tms_data: List[Dict[str, Any]],
        carrier_quotes: List[Dict[str, Any]],
        traffic: Dict[str, Any],
        weather: Dict[str, Any]
    ) -> Dict[str, Any]:
        """路径优化"""
        await asyncio.sleep(0.3)

        routes = []
        total_cost = 0

        for order in tms_data:
            route = {
                "order_id": order["order_id"],
                "carrier": carrier_quotes[0]["name"],
                "distance": 600 if order["destination"] == "上海" else 500,
                "cost": 2100 if order["destination"] == "上海" else 1600,
                "eta": "14:00" if order["destination"] == "上海" else "12:00"
            }
            routes.append(route)
            total_cost += route["cost"]

        return {
            "routes": routes,
            "total_cost": total_cost
        }

    async def _calculate_load_balance(self, route_result: Dict[str, Any]) -> Dict[str, Any]:
        """装载率优化"""
        return {
            "average_utilization": 0.72,
            "vehicles_below_60_percent": [],
            "recommendation": "当前装载率良好，无需调整"
        }

    async def validate_constraints(self, output: AgentOutput) -> bool:
        """验证约束"""
        compliance = output.data.get("compliance_check", {})
        return compliance.get("passed", False)