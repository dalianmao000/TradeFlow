# TradeFlow AI Agent

多智能体 AI 系统 - 化工贸易智能自动化解决方案，支持人机协同治理

## 开发状态

### ✅ 已完成

| 模块 | 状态 | 说明 |
|:---|:---:|:---|
| **架构设计** | ✅ 完成 | 5层架构：交互层 → 编排层 → Agent集群 → 工具层 → 数据层 |
| **Agent框架** | ✅ 完成 | 6个Agent实现（中枢 + 5个垂直业务Agent） |
| **LangGraph集成** | ✅ 完成 | 所有Agent的状态机配置 |
| **MCP服务器** | ✅ 完成 | 协议 + 4个服务（RAG、ML、优化、图谱） |
| **FastAPI后端** | ✅ 完成 | REST API，涵盖所有Agent接口 |
| **Docker支持** | ✅ 完成 | 多阶段Dockerfile + docker-compose |
| **Kubernetes支持** | ✅ 完成 | 基础部署配置（Deployment、Service、ConfigMap） |
| **项目脚手架** | ✅ 完成 | 完整目录结构、依赖、配置文件 |
| **技术文档** | ✅ 完成 | 架构设计、MCP接口规范、Agent配置 |

### 🚧 进行中

| 模块 | 状态 | 说明 |
|:---|:---:|:---|
| **单元测试** | 🚧 待开发 | Agent单元测试、MCP服务测试、API集成测试 |
| **CI/CD流水线** | 🚧 待开发 | GitHub Actions 工作流（构建/测试/部署） |

### 📋 未来开发计划

| 模块 | 优先级 | 说明 |
|:---|:---:|:---|
| **生产级数据库集成** | P1 | PostgreSQL（Agent状态）、TimescaleDB（时序数据） |
| **向量数据库集成** | P1 | Milvus（RAG语义检索） |
| **图数据库集成** | P1 | NebulaGraph（知识图谱关系） |
| **大语言模型集成** | P1 | 连接通义千问/DeepSeek API |
| **实时数据源对接** | P2 | 行情数据API、新闻舆情、天气数据 |
| **前端控制台** | P2 | Web监控界面与Agent控制面板 |
| **高级机器学习模型** | P2 | 价格预测（LightGBM/Prophet）、异常检测 |
| **运筹优化求解器** | P2 | Gurobi/OR-Tools 生产排程集成 |
| **告警监控系统** | P2 | Prometheus + Grafana 监控、钉钉/企微通知 |
| **多租户支持** | P3 | RBAC权限、租户隔离、配额管理 |
| **联邦学习** | P3 | 跨伙伴隐私保护模型训练 |

---

## 项目结构

```
tradflow-ai-agent/
├── src/
│   ├── agents/          # 6个Agent：中枢 + 5个垂直业务Agent
│   ├── mcp/             # MCP服务器实现
│   │   └── services/    # RAG/ML/优化/图谱服务
│   ├── core/            # 核心组件（配置/状态/工具/记忆）
│   └── api/             # FastAPI入口
├── docker/              # Docker配置
├── k8s/                 # Kubernetes部署配置
├── configs/             # Agent和服务配置
├── tests/               # 测试
└── scripts/             # 脚本
```

## 快速开始

### 1. 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动API服务
python -m src.api.main

# 启动MCP服务
python -m src.mcp.server
```

### 2. Docker运行

```bash
# 构建镜像
docker build -f docker/Dockerfile.agent -t tradflow-ai-agent:latest .

# 运行容器
docker run -p 8000:8000 tradflow-ai-agent:latest
```

### 3. Kubernetes部署

```bash
# 应用基础配置
kubectl apply -f k8s/base/

# 应用开发环境配置
kubectl apply -f k8s/overlays/dev/
```

## API接口

| 接口 | 方法 | 说明 |
|:---|:---|:---|
| `/api/v1/agent/execute` | POST | 中枢Agent路由入口 |
| `/api/v1/agent/price_prediction` | POST | 市场价格预测 |
| `/api/v1/agent/customer_recommend` | POST | 客户智能推荐 |
| `/api/v1/agent/production_optimize` | POST | 产销协同优化 |
| `/api/v1/agent/supply_chain_schedule` | POST | 供应链调度 |
| `/api/v1/agent/risk_monitor` | POST | 风控预警 |
| `/health` | GET | 健康检查 |

## Agent列表

| Agent | 功能 |
|:---|:---|
| `central` | 中枢Agent - 意图识别、任务路由 |
| `price_prediction` | 市场价格预测 |
| `customer_recommend` | 客户智能推荐 |
| `production_sales` | 产销协同优化 |
| `supply_chain` | 供应链调度 |
| `risk_control` | 风控预警 |

## 系统架构

- **5层架构**：交互层 → 编排层 → Agent集群 → 工具层 → 数据层
- **多Agent协同**：并行执行 + 结果汇总
- **人机协同**：关键决策可配置审批流程
- **企业级特性**：RBAC权限、审计日志、数据分级

## 技术栈

- Python 3.11+
- FastAPI + LangGraph
- PostgreSQL + Milvus + NebulaGraph
- Docker + Kubernetes
- Prometheus + Grafana

## 许可证

MIT License - Copyright (c) 2026 dalianmao000