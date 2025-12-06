from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
from loguru import logger

from app.core.database import get_db
from app.schemas.package import (
    PackageUploadRequest,
    PackageRecordResponse,
    PackageHistoryResponse
)
from app.services.package_service import PackageService
from app.repositories.package_repository import PackageRepository

router = APIRouter()


def get_package_service(db: Session = Depends(get_db)) -> PackageService:
    """依赖注入：获取包裹服务"""
    repository = PackageRepository(db)
    return PackageService(repository)


@router.post("/upload", response_model=Dict[str, Any], tags=["Package"])
async def upload_package_data(
    payload: PackageUploadRequest,
    service: PackageService = Depends(get_package_service)
):
    """
    接收 ESP32 上传的 RFID 包裹数据
    
    - **package_id**: 包裹ID（正整数）
    - **max_temperature**: 最高温度值（-50 ~ 100°C）
    - **avg_humidity**: 平均湿度值（0 ~ 100%）
    - **over_threshold_time**: 超阈值时间（秒）
    - **timestamp**: Unix时间戳（秒）
    """
    try:
        result = service.save_package_data(payload)
        return result
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages/{package_id}/records", response_model=PackageHistoryResponse, tags=["Package"])
async def get_package_history(
    package_id: int,
    limit: int = Query(default=100, ge=1, le=1000, description="返回记录数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    service: PackageService = Depends(get_package_service)
):
    """
    查询指定包裹的历史温度记录
    
    - **package_id**: 包裹ID
    - **limit**: 返回记录数量（1-1000）
    - **offset**: 偏移量（用于分页）
    """
    try:
        history = service.get_package_history(package_id, limit, offset)
        return history
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages/{package_id}/latest", response_model=PackageRecordResponse, tags=["Package"])
async def get_latest_record(
    package_id: int,
    service: PackageService = Depends(get_package_service)
):
    """
    获取指定包裹的最新温度记录
    
    - **package_id**: 包裹ID
    """
    try:
        record = service.get_latest_record(package_id)
        if not record:
            raise HTTPException(
                status_code=404, 
                detail=f"No records found for package {package_id}"
            )
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
