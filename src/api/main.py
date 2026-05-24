"""FastAPI主入口"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import router
from ..core.config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载配置
config = load_config()

# 创建FastAPI应用
app = FastAPI(
    title=config.app_name,
    version="1.0.0",
    description="TradeFlow AI Agent API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(exc)
            }
        }
    )


# 健康检查
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": config.app_name
    }


# 注册路由
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {config.app_name} in {config.environment} mode")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {config.app_name}")