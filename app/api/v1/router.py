from fastapi import APIRouter
from app.api.v1.endpoints import package, health, auth, user_packages, monitor, device

# 创建 v1 版本的主路由
api_router = APIRouter()

# 包含各个端点的路由
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(package.router, prefix="", tags=["Package"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user_packages.router, prefix="/packages", tags=["User Packages"])
# monitor 路由已移除 - 只保留 packages/{id}/records 接口
# api_router.include_router(monitor.router, prefix="/monitor", tags=["Data Monitor"])
api_router.include_router(device.router, prefix="", tags=["Device"])
