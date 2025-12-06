from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router
from app.utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    setup_logger()
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME}")
    logger.info(f"📌 Version: {settings.API_VERSION}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info("=" * 60)
    
    # 初始化数据库
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
    
    yield
    
    # 关闭时执行
    logger.info("🛑 Shutting down application")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="ESP32 RFID 物流包裹温控数据采集系统后端 API",
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json"
)

# 配置 CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.API_VERSION,
        "docs": f"/api/{settings.API_VERSION}/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )
