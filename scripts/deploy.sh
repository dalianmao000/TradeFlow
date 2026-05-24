#!/bin/bash
set -e

echo "Deploying TradeFlow AI Agent to Kubernetes..."

# 构建镜像
docker build -f docker/Dockerfile.agent -t tradflow-ai-agent:latest .

# 打标签
docker tag tradflow-ai-agent:latest registry.example.com/tradflow-ai-agent:latest

# 推送镜像（需要配置registry）
# docker push registry.example.com/tradflow-ai-agent:latest

# 应用配置
kubectl apply -f k8s/base/

# 等待部署
kubectl rollout status deployment/tradflow-api

echo "Deployment completed!"