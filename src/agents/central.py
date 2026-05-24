"""中枢Agent - 意图识别、任务路由、状态管理"""
from typing import Any, Dict, List, Optional
from .base import BaseAgent, AgentOutput
import re


class CentralAgent(BaseAgent):
    """AI业务中枢Agent"""

    def __init__(self):
        super().__init__(
            agent_id="central",
            name="AI业务中枢Agent",
            role="意图识别、任务路由、状态管理、异常熔断、人机协同"
        )

        # 意图识别映射
        self.intent_map = {
            "price_query": ["price_prediction"],
            "recommend_request": ["customer_recommend"],
            "production_optimize": ["production_sales"],
            "schedule_request": ["supply_chain"],
            "risk_alert": ["risk_control"],
        }

        # 复杂决策 - 多Agent协同
        self.complex_intents = {
            "lock_price_decision": ["price_prediction", "customer_recommend", "risk_control"],
            "production_adjustment": ["production_sales", "supply_chain", "risk_control"],
        }

        # HITL规则 - 需要人工介入的条件
        self.hitl_rules = [
            ("amount_over_10m", lambda x: x.get("amount", 0) > 10000000),
            ("price_volatility_over_5pct", lambda x: x.get("price_volatility", 0) > 0.05),
            ("new_customer_first_time", lambda x: x.get("is_new_customer", False)),
            ("blacklist_customer", lambda x: x.get("is_blacklist", False)),
        ]

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """解析意图并路由到对应Agent"""
        user_input = input_data.get("query", "")
        context = input_data.get("context", {})

        # 意图识别
        intent = self._recognize_intent(user_input)
        target_agents = self._get_target_agents(intent, user_input)

        # 检查是否需要人工介入
        requires_review = self._check_hitl_rules(context)

        # 构建路由决策
        routing_decision = {
            "intent": intent,
            "target_agents": target_agents,
            "requires_human_review": requires_review,
            "context": context
        }

        reasoning = f"识别到意图: {intent}，路由到: {', '.join(target_agents)}"
        if requires_review:
            reasoning += "（触发人工介入规则）"

        return self._create_output(
            status="success",
            confidence=0.95,
            data={"routing": routing_decision},
            reasoning=reasoning,
            requires_human_review=requires_review
        )

    def _recognize_intent(self, user_input: str) -> str:
        """识别用户意图"""
        user_input_lower = user_input.lower()

        # 价格查询相关
        price_keywords = ["价格", "预测", "走势", "基差", "期货", "现货"]
        if any(kw in user_input_lower for kw in price_keywords):
            return "price_query"

        # 推荐相关
        recommend_keywords = ["推荐", "客户", "潜客", "交叉销售"]
        if any(kw in user_input_lower for kw in recommend_keywords):
            return "recommend_request"

        # 产销相关
        production_keywords = ["排产", "产销", "库存", "订单"]
        if any(kw in user_input_lower for kw in production_keywords):
            return "production_optimize"

        # 供应链相关
        supply_keywords = ["调度", "物流", "运输", "路线"]
        if any(kw in user_input_lower for kw in supply_keywords):
            return "schedule_request"

        # 风控相关
        risk_keywords = ["风险", "预警", "信用", "VaR"]
        if any(kw in user_input_lower for kw in risk_keywords):
            return "risk_alert"

        # 复合决策检测
        if "锁价" in user_input_lower or "采购" in user_input_lower:
            return "lock_price_decision"

        return "unknown"

    def _get_target_agents(self, intent: str, user_input: str) -> List[str]:
        """获取目标Agent列表"""
        # 检查复杂意图
        if intent in self.complex_intents:
            return self.complex_intents[intent]

        # 单Agent意图
        if intent in self.intent_map:
            return self.intent_map[intent]

        return []

    def _check_hitl_rules(self, context: Dict[str, Any]) -> bool:
        """检查是否需要人工介入"""
        for rule_name, rule_func in self.hitl_rules:
            if rule_func(context):
                self.logger.info(f"HITL rule triggered: {rule_name}")
                return True
        return False

    async def validate_constraints(self, output: AgentOutput) -> bool:
        """中枢Agent的约束验证"""
        # 中枢Agent主要负责路由，约束验证由下游Agent执行
        return True

    async def aggregate_results(
        self,
        agent_outputs: List[AgentOutput]
    ) -> AgentOutput:
        """汇总多个Agent的结果"""
        combined_data = {"agent_results": [o.to_dict() for o in agent_outputs]}

        # 计算平均置信度
        avg_confidence = sum(o.confidence for o in agent_outputs) / len(agent_outputs)

        # 检查是否有Agent需要人工复核
        requires_review = any(o.requires_human_review for o in agent_outputs)

        return self._create_output(
            status="success",
            confidence=avg_confidence,
            data=combined_data,
            reasoning=f"汇总了{len(agent_outputs)}个Agent的结果",
            requires_human_review=requires_review
        )