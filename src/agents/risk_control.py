"""风控预警Agent"""
from typing import Any, Dict, List
from .base import BaseAgent, AgentOutput
import asyncio


class RiskControlAgent(BaseAgent):
    """风控预警Agent"""

    def __init__(self):
        super().__init__(
            agent_id="risk_control",
            name="风控预警Agent",
            role="市场/信用/合同/操作风险实时监测",
            tools=[
                "get_price_data",
                "calculate_var",
                "get_credit_data",
                "run_anomaly_detection",
                "analyze_contract",
                "check_sanction_list",
                "build_kg_relations",
                "send_alert"
            ],
            constraints=[
                "高风险事件 → 自动升级至风控总监",
                "所有预警留痕可追溯",
                "黑样本少场景 → 规则+模型混合判断",
                "预警误报率 > 20% → 自动触发模型重训"
            ]
        )

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """执行风控预警"""
        monitor_type = input_data.get("monitor_type", "all")  # market, credit, contract, all

        self.logger.info(f"执行风控预警: {monitor_type}")

        try:
            alerts = []

            # 市场风险监测
            if monitor_type in ["market", "all"]:
                market_alert = await self._monitor_market()
                if market_alert:
                    alerts.append(market_alert)

            # 信用风险监测
            if monitor_type in ["credit", "all"]:
                credit_alert = await self._monitor_credit()
                if credit_alert:
                    alerts.append(credit_alert)

            # 合同风险监测
            if monitor_type in ["contract", "all"]:
                contract_alerts = await self._monitor_contracts()
                alerts.extend(contract_alerts)

            # 计算风险指标
            risk_metrics = await self._calculate_risk_metrics(alerts)

            reasoning = f"监测完成：{len(alerts)}条预警，"
            if alerts:
                high_risk = sum(1 for a in alerts if a["level"] == "high")
                reasoning += f"其中高风险{high_risk}条"
            else:
                reasoning += "无异常"

            requires_review = any(a["level"] == "high" for a in alerts)

            return self._create_output(
                status="success",
                confidence=0.85,
                data={
                    "alerts": alerts,
                    "risk_metrics": risk_metrics
                },
                reasoning=reasoning,
                requires_human_review=requires_review
            )

        except Exception as e:
            self.logger.error(f"风控预警失败: {e}")
            return self._create_output(
                status="failed",
                confidence=0.0,
                data={"error": str(e)},
                reasoning=f"预警失败: {str(e)}",
                requires_human_review=True
            )

    async def _monitor_market(self) -> Optional[Dict[str, Any]]:
        """监测市场价格"""
        await asyncio.sleep(0.1)

        # 模拟价格波动检测
        price_data = await self._get_price_data()
        var = await self._calculate_var(price_data)

        # 检测异常波动
        if abs(price_data["volatility"]) > 0.03:
            return {
                "alert_id": "M001",
                "risk_type": "market",
                "level": "medium",
                "description": f"PX价格波动{price_data['volatility']:.1%}，超过阈值3%",
                "affected_entities": ["PX现货", "PX期货"],
                "recommended_actions": ["加强监测", "考虑套保"],
                "var_impact": var
            }

        return None

    async def _monitor_credit(self) -> Optional[Dict[str, Any]]:
        """监测客户信用"""
        await asyncio.sleep(0.1)

        credit_data = await self._get_credit_data()

        if credit_data["exposure_ratio"] > 0.8:
            return {
                "alert_id": "C001",
                "risk_type": "credit",
                "level": "high",
                "description": f"客户{credit_data['customer_name']}信用敞口比例{credit_data['exposure_ratio']:.1%}",
                "affected_entities": [credit_data["customer_id"]],
                "recommended_actions": ["收紧授信", "催收欠款"],
                "var_impact": credit_data["var"]
            }

        return None

    async def _monitor_contracts(self) -> List[Dict[str, Any]]:
        """监测合同履约"""
        await asyncio.sleep(0.1)
        # 模拟返回
        return []

    async def _get_price_data(self) -> Dict[str, Any]:
        """获取价格数据"""
        return {
            "product": "PX",
            "current_price": 8500,
            "volatility": 0.035,
            "var_95": 250000
        }

    async def _calculate_var(self, price_data: Dict[str, Any]) -> float:
        """计算VaR"""
        return price_data.get("var_95", 0)

    async def _get_credit_data(self) -> Dict[str, Any]:
        """获取征信数据"""
        return {
            "customer_id": "C001",
            "customer_name": "客户A",
            "credit_limit": 5000000,
            "credit_used": 4500000,
            "exposure_ratio": 0.90,
            "var": 500000
        }

    async def _calculate_risk_metrics(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算风险指标"""
        return {
            "portfolio_var": 1500000,
            "credit_exposure": 8500000,
            "compliance_score": 0.95,
            "alert_count_today": len(alerts)
        }

    async def validate_constraints(self, output: AgentOutput) -> bool:
        """验证约束"""
        # 高风险事件必须升级
        alerts = output.data.get("alerts", [])
        for alert in alerts:
            if alert["level"] == "high" and not output.requires_human_review:
                self.logger.warning(f"高风险事件未标记人工介入: {alert['alert_id']}")
                return False

        return True