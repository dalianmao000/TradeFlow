"""产销协同优化Agent"""
from typing import Any, Dict, List
from .base import BaseAgent, AgentOutput
import asyncio


class ProductionSalesAgent(BaseAgent):
    """产销协同优化Agent"""

    def __init__(self):
        super().__init__(
            agent_id="production_sales",
            name="产销协同优化Agent",
            role="库存-订单-产能动态平衡与排产建议",
            tools=[
                "query_ubmp_orders",
                "query_production_plan",
                "query_inventory",
                "run_optimizer",
                "check_business_rules",
                "whatif_analysis"
            ],
            constraints=[
                "硬约束：最小起订量、质检周期、交割标准 → 100%满足",
                "软约束：成本最低 → 多目标权衡 + Pareto前沿展示",
                "交期冲突时 → 自动生成妥协方案"
            ]
        )

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """执行产销协同优化"""
        self.logger.info("执行产销协同优化")

        try:
            # 1. 获取订单数据
            orders = await self._query_orders()

            # 2. 获取排产计划
            production_plans = await self._query_production_plan()

            # 3. 获取库存
            inventory = await self._query_inventory()

            # 4. 运筹优化
            optimization_result = await self._run_optimizer(
                orders, production_plans, inventory
            )

            # 5. 规则校验
            validation = await self._check_business_rules(optimization_result)

            if not validation["passed"]:
                # 触发What-if分析
                whatif_result = await self._whatif_analysis(
                    optimization_result, validation["violations"]
                )
                optimization_result["whatif_adjustment"] = whatif_result

            reasoning = f"优化完成：履约率={optimization_result['metrics']['fulfillment_rate']:.1%}"
            reasoning += f"，总成本={optimization_result['metrics']['total_cost']}元"

            return self._create_output(
                status="success",
                confidence=0.92,
                data={
                    "assignments": optimization_result["assignments"],
                    "unfulfilled": optimization_result.get("unfulfilled", []),
                    "metrics": optimization_result["metrics"],
                    "pareto_front": optimization_result.get("pareto_front", []),
                    "validation": validation
                },
                reasoning=reasoning,
                requires_human_review=not validation["passed"]
            )

        except Exception as e:
            self.logger.error(f"产销协同优化失败: {e}")
            return self._create_output(
                status="failed",
                confidence=0.0,
                data={"error": str(e)},
                reasoning=f"优化失败: {str(e)}",
                requires_human_review=True
            )

    async def _query_orders(self) -> List[Dict[str, Any]]:
        """查询订单池"""
        await asyncio.sleep(0.1)
        return [
            {"id": "O001", "product": "PX", "quantity": 500, "due_date": "2024-05-10"},
            {"id": "O002", "product": "MX", "quantity": 300, "due_date": "2024-05-12"},
            {"id": "O003", "product": "PX", "quantity": 200, "due_date": "2024-05-15"},
        ]

    async def _query_production_plan(self) -> List[Dict[str, Any]]:
        """查询排产计划"""
        await asyncio.sleep(0.1)
        return [
            {"line": "L1", "product": "PX", "capacity": 1000, "setup_cost": 5000},
            {"line": "L2", "product": "MX", "capacity": 800, "setup_cost": 4500},
        ]

    async def _query_inventory(self) -> List[Dict[str, Any]]:
        """查询库存"""
        await asyncio.sleep(0.1)
        return [
            {"product": "PX", "warehouse": "W1", "quantity": 300},
            {"product": "MX", "warehouse": "W1", "quantity": 150},
        ]

    async def _run_optimizer(
        self,
        orders: List[Dict[str, Any]],
        production_plans: List[Dict[str, Any]],
        inventory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """运行优化求解器"""
        await asyncio.sleep(0.3)

        # 模拟优化结果
        assignments = []
        for order in orders:
            assignments.append({
                "order_id": order["id"],
                "line": "L1" if order["product"] == "PX" else "L2",
                "quantity": order["quantity"],
                "cost": order["quantity"] * 9,
                "due_date": order["due_date"]
            })

        return {
            "status": "optimal",
            "assignments": assignments,
            "unfulfilled": [],
            "metrics": {
                "total_cost": 8500,
                "fulfillment_rate": 1.0,
                "inventory_turns": 2.3
            },
            "pareto_front": [
                {"cost": 8000, "fulfillment": 0.92},
                {"cost": 8500, "fulfillment": 1.0},
                {"cost": 9000, "fulfillment": 1.0}
            ]
        }

    async def _check_business_rules(self, optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """校验业务规则"""
        violations = []

        for assignment in optimization_result["assignments"]:
            # 检查最小起订量
            if assignment["quantity"] < 100:
                violations.append(f"订单{assignment['order_id']}违反最小起订量规则")

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    async def _whatif_analysis(
        self,
        original_result: Dict[str, Any],
        violations: List[str]
    ) -> Dict[str, Any]:
        """What-if情景分析"""
        await asyncio.sleep(0.2)

        return {
            "scenario": "放松部分约束",
            "adjusted_assignments": original_result["assignments"],
            "tradeoff": "成本↑5%，但可满足全部订单"
        }

    async def validate_constraints(self, output: AgentOutput) -> bool:
        """验证约束"""
        validation = output.data.get("validation", {})
        return validation.get("passed", False)