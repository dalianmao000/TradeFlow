"""客户智能推荐Agent"""
from typing import Any, Dict, List
from .base import BaseAgent, AgentOutput
import asyncio


class CustomerRecommendAgent(BaseAgent):
    """客户智能推荐Agent"""

    def __init__(self):
        super().__init__(
            agent_id="customer_recommend",
            name="客户智能推荐Agent",
            role="B2B潜客挖掘与交叉销售策略生成",
            tools=[
                "query_crm",
                "get_transaction_history",
                "run_recommendation_model",
                "filter_blacklist",
                "generate_personalized_content"
            ],
            constraints=[
                "授信额度不足 → 直接过滤",
                "黑名单客户 → 直接过滤",
                "输出必须包含推荐理由（特征贡献度）"
            ]
        )

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """执行客户推荐"""
        product = input_data.get("product", "PX")
        top_n = input_data.get("top_n", 10)

        self.logger.info(f"执行客户推荐: 产品={product}, Top-{top_n}")

        try:
            # 1. 查询CRM数据
            crm_data = await self._query_crm(product)

            # 2. 获取历史交易
            transaction_history = await self._get_transaction_history(product)

            # 3. 过滤黑名单和授信不足客户
            filtered_customers = await self._filter_blacklist(crm_data)

            # 4. 运行推荐模型
            recommendations = await self._run_recommendation_model(
                filtered_customers, transaction_history, top_n
            )

            # 5. 生成触达策略
            strategy = await self._generate_strategy(recommendations)

            reasoning = f"为{product}生成了{len(recommendations)}条客户推荐"

            return self._create_output(
                status="success",
                confidence=0.88,
                data={
                    "recommendations": recommendations,
                    "strategy": strategy,
                    "total_candidates": len(crm_data),
                    "filtered_count": len(crm_data) - len(filtered_customers)
                },
                reasoning=reasoning,
                requires_human_review=False
            )

        except Exception as e:
            self.logger.error(f"客户推荐失败: {e}")
            return self._create_output(
                status="failed",
                confidence=0.0,
                data={"error": str(e)},
                reasoning=f"推荐失败: {str(e)}",
                requires_human_review=True
            )

    async def _query_crm(self, product: str) -> List[Dict[str, Any]]:
        """查询CRM客户数据"""
        await asyncio.sleep(0.1)
        # 模拟返回客户列表
        return [
            {"customer_id": "C001", "name": "客户A", "credit_limit": 5000000, "credit_used": 3000000},
            {"customer_id": "C002", "name": "客户B", "credit_limit": 3000000, "credit_used": 2800000},
            {"customer_id": "C003", "name": "客户C", "credit_limit": 8000000, "credit_used": 2000000},
        ]

    async def _get_transaction_history(self, product: str) -> List[Dict[str, Any]]:
        """获取历史交易"""
        await asyncio.sleep(0.1)
        return [
            {"customer_id": "C001", "product": product, "volume": 500, "last_order_date": "2024-04-15"},
            {"customer_id": "C003", "product": product, "volume": 800, "last_order_date": "2024-04-20"},
        ]

    async def _filter_blacklist(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤黑名单和授信不足客户"""
        filtered = []
        for c in customers:
            # 授信额度检查
            available = c["credit_limit"] - c["credit_used"]
            if available < 100000:  # 可用额度不足
                self.logger.info(f"过滤授信不足客户: {c['customer_id']}")
                continue

            # 黑名单检查（模拟）
            if c["customer_id"] == "C002":
                self.logger.info(f"过滤黑名单客户: {c['customer_id']}")
                continue

            filtered.append(c)

        return filtered

    async def _run_recommendation_model(
        self,
        customers: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        top_n: int
    ) -> List[Dict[str, Any]]:
        """运行推荐模型"""
        await asyncio.sleep(0.2)

        # 构建客户-交易映射
        transaction_map = {t["customer_id"]: t for t in transactions}

        recommendations = []
        for customer in customers[:top_n]:
            trans = transaction_map.get(customer["customer_id"], {})

            rec = {
                "customer_id": customer["customer_id"],
                "customer_name": customer["name"],
                "recommended_products": ["PX", "MX"],
                "expected_conversion_rate": 0.75,
                "potential_volume": 500,
                "reason": "历史交易活跃 + 授信充足",
                "feature_importance": {
                    "transaction_frequency": 0.35,
                    "credit_available": 0.30,
                    "product_affinity": 0.25,
                    "region_proximity": 0.10
                }
            }
            recommendations.append(rec)

        return recommendations

    async def _generate_strategy(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成触达策略"""
        return {
            "channel": "企业微信",
            "content_template": "尊敬的{customer_name}，{product}近期行情分析...",
            "follow_up_timing": "工作日上午10-11点",
            "discount_available": True
        }

    async def validate_constraints(self, output: AgentOutput) -> bool:
        """验证约束"""
        recommendations = output.data.get("recommendations", [])

        for rec in recommendations:
            if rec.get("expected_conversion_rate", 0) < 0.5:
                self.logger.warning(f"推荐置信度过低: {rec['customer_id']}")
                return False

        return True