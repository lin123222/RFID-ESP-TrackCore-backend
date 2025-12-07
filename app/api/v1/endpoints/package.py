from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from loguru import logger

from app.core.database import get_db
from app.schemas.package import (
    PackageUploadRequest,
    PackageHistoryResponse
)
from app.schemas.user import TokenData
from app.services.package_service import PackageService
from app.repositories.package_repository import PackageRepository
from app.repositories.user import UserPackageRepository
from app.api.deps import verify_device_authentication, get_current_user
from app.models.device import Device

router = APIRouter()


def get_package_service(db: Session = Depends(get_db)) -> PackageService:
    """依赖注入：获取包裹服务"""
    repository = PackageRepository(db)
    return PackageService(repository)


def get_user_package_repository(db: Session = Depends(get_db)) -> UserPackageRepository:
    """依赖注入：获取用户包裹关联仓库"""
    return UserPackageRepository(db)


@router.post("/upload", response_model=Dict[str, Any], tags=["Package"])
async def upload_package_data(
    payload: PackageUploadRequest,
    device: Device = Depends(verify_device_authentication),  # 添加设备认证
    service: PackageService = Depends(get_package_service)
):
    """
    接收 ESP32 上传的 RFID 包裹数据（需要设备认证）
    
    请求头要求：
    - **X-Device-ID**: 设备唯一标识（如：ESP32-001）
    - **X-Signature**: HMAC-SHA256 签名
    - **X-Timestamp**: Unix时间戳（秒）
    
    请求体：
    - **package_id**: 包裹ID（正整数）
    - **max_temperature**: 最高温度值（-50 ~ 100°C）
    - **avg_humidity**: 平均湿度值（0 ~ 100%）
    - **over_threshold_time**: 超阈值时间（秒）
    - **timestamp**: Unix时间戳（秒）
    """
    try:
        result = service.save_package_data(payload)
        logger.info(f"Data uploaded by device: {device.device_id}")
        return result
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages/{package_id}/records", response_model=PackageHistoryResponse, tags=["Package"])
async def get_package_history(
    package_id: int,
    limit: int = Query(default=1000, ge=1, le=10000, description="返回记录数量（默认1000，最大10000）"),
    offset: int = Query(default=0, ge=0, description="偏移量（用于分页）"),
    current_user: TokenData = Depends(get_current_user),  # 需要用户登录
    service: PackageService = Depends(get_package_service),
    user_package_repo: UserPackageRepository = Depends(get_user_package_repository)
):
    """
    获取包裹的所有站点记录（需要登录，只能查看自己的包裹）
    
    返回包裹在运输过程中到达各个站点后记录的数据：
    - 每条记录包含：最大温度、平均湿度、超阈值时间、时间戳
    
    - **package_id**: 包裹ID
    - **limit**: 返回记录数量（1-10000，默认1000）
    - **offset**: 偏移量（用于分页，默认0）
    
    权限要求：
    - 需要JWT Token认证
    - 只能查看已绑定到自己账户的包裹数据
    
    返回数据按时间倒序排列（最新的在前）
    """
    # 检查包裹所有权
    if not user_package_repo.check_package_ownership(current_user.user_id, package_id):
        logger.warning(
            f"User {current_user.user_id} attempted to access package {package_id} "
            f"without ownership"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You don't have permission to view package {package_id}"
        )
    
    try:
        history = service.get_package_history(package_id, limit, offset)
        logger.info(
            f"User {current_user.user_id} (username: {current_user.username}) "
            f"queried package {package_id} history"
        )
        return history
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


