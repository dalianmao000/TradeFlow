"""市场价格预测Agent"""
from typing import Any, Dict, List
from .base import BaseAgent, AgentOutput
import asyncio


class PricePredictionAgent(BaseAgent):
    """市场洞察与价格预测Agent"""

    def __init__(self):
        super().__init__(
            agent_id="price_prediction",
            name="市场洞察与价格预测Agent",
            role="期现基差分析与价格趋势推演",
            tools=[
                "fetch_market_data",
                "fetch_macro_data",
                "run_price_model",
                "calculate_confidence",
                "generate_report"
            ],
            constraints=[
                "MAPE > 30% → 自动降低权重 + 触发人工复核",
                "极端行情（±5%波动）→ 禁用自动执行 + 全量人工审批",
                "输出必须附带回测误差区间"
            ]
        )

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """执行价格预测"""
        product = input_data.get("product", "PX")
        region = input_data.get("region", "华东")
        horizon_days = input_data.get("horizon_days", 7)

        self.logger.info(f"执行价格预测: {product} {region} {horizon_days}天")

        # 模拟执行流程
        try:
            # 1. 获取市场数据
            market_data = await self._fetch_market_data(product, region)

            # 2. 获取宏观数据
            macro_data = await self._fetch_macro_data()

            # 3. 运行预测模型
            prediction = await self._run_price_model(
                product, region, horizon_days, market_data, macro_data
            )

            # 4. 计算置信度
            confidence = await self._calculate_confidence(prediction)

            # 5. 检查约束
            requires_review = self._check_review_requirements(
                prediction, market_data
            )

            reasoning = f"预测{product}未来{horizon_days}日均价为{prediction['price']}元/吨"
            reasoning += f"，MAPE={prediction.get('backtest', {}).get('MAPE', 'N/A')}"

            return self._create_output(
                status="success",
                confidence=confidence,
                data={
                    "prediction": prediction,
                    "market_data": market_data,
                    "macro_data": macro_data
                },
                reasoning=reasoning,
                requires_human_review=requires_review
            )

        except Exception as e:
            self.logger.error(f"价格预测失败: {e}")
            return self._create_output(
                status="failed",
                confidence=0.0,
                data={"error": str(e)},
                reasoning=f"预测失败: {str(e)}",
                requires_human_review=True
            )

    async def _fetch_market_data(self, product: str, region: str) -> Dict[str, Any]:
        """获取市场数据"""
        # 模拟实现 - 实际应调用MCP服务
        await asyncio.sleep(0.1)
        return {
            "current_price": 8500,
            "inventory_level": 0.65,
            "port_throughput": 85000,
            "historical_prices": [8450, 8480, 8520, 8500, 8490]
        }

    async def _fetch_macro_data(self) -> Dict[str, Any]:
        """获取宏观数据"""
        await asyncio.sleep(0.1)
        return {
            "macro_index": 102.5,
            "原油价格": 75.5,
            "汇率": 7.24
        }

    async def _run_price_model(
        self,
        product: str,
        region: str,
        horizon_days: int,
        market_data: Dict[str, Any],
        macro_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行价格预测模型"""
        await asyncio.sleep(0.2)

        # 模拟预测结果
        current = market_data["current_price"]
        prediction_price = current * 1.015  # 模拟上涨1.5%

        return {
            "product": product,
            "region": region,
            "horizon_days": horizon_days,
            "price": round(prediction_price, 2),
            "lower_bound": round(prediction_price * 0.97, 2),
            "upper_bound": round(prediction_price * 1.03, 2),
            "confidence": 0.85,
            "directional_accuracy": 0.78,
            "factor_attribution": {
                "inventory_level": 0.32,
                "macro_index": 0.28,
                "historical_prices": 0.25,
                "port_throughput": 0.15
            },
            "backtest": {
                "MAPE": 0.048,
                "WAPE": 0.042,
                "sharpe_ratio": 1.35
            }
        }

    async def _calculate_confidence(self, prediction: Dict[str, Any]) -> float:
        """计算预测置信度"""
        backtest_mape = prediction.get("backtest", {}).get("MAPE", 1.0)
        # MAPE越低，置信度越高
        confidence = max(0.0, min(1.0, 1.0 - backtest_mape * 5))
        return round(confidence, 2)

    def _check_review_requirements(
        self,
        prediction: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> bool:
        """检查是否需要人工复核"""
        # 检查MAPE
        mape = prediction.get("backtest", {}).get("MAPE", 0)
        if mape > 0.30:
            return True

        # 检查极端行情
        current = market_data.get("current_price", 0)
        pred_price = prediction.get("price", 0)
        if current > 0:
            volatility = abs(pred_price - current) / current
            if volatility > 0.05:
                return True

        return False

    async def validate_constraints(self, output: AgentOutput) -> bool:
        """验证业务约束"""
        if not output.constraints_satisfied:
            return False

        # MAPE约束
        mape = output.data.get("prediction", {}).get("backtest", {}).get("MAPE", 1.0)
        if mape > 0.30:
            self.logger.warning(f"MAPE约束不满足: {mape} > 0.30")
            return False

        return True