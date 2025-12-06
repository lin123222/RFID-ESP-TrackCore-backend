from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from app.schemas.monitor import (
    PackageDetailResponse, PackageRecordsResponse, DetailedStatisticsResponse
)
from app.schemas.common import SuccessResponse
from app.services.monitor import MonitorService
from app.api.deps import get_current_user
from app.schemas.user import TokenData
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()


def get_monitor_service(db: Session = Depends(get_db)) -> MonitorService:
    """获取监控服务实例"""
    return MonitorService(db)


@router.get("/{package_id}", response_model=SuccessResponse[PackageDetailResponse])
async def get_package_detail(
    package_id: int,
    current_user: TokenData = Depends(get_current_user),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """
    获取包裹详情
    
    - **package_id**: 包裹ID
    """
    package_detail = monitor_service.get_package_detail(current_user.user_id, package_id)
    return SuccessResponse(
        message="获取成功",
        data=package_detail
    )


@router.get("/{package_id}/records", response_model=SuccessResponse[PackageRecordsResponse])
async def get_package_records(
    package_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(100, ge=1, le=1000, description="每页数量"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: TokenData = Depends(get_current_user),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """
    获取包裹历史记录
    
    - **package_id**: 包裹ID
    - **page**: 页码 (从1开始)
    - **size**: 每页数量 (1-1000)
    - **start_date**: 开始日期 (可选)
    - **end_date**: 结束日期 (可选)
    """
    records = monitor_service.get_package_records(
        current_user.user_id, package_id, page, size, start_date, end_date
    )
    return SuccessResponse(
        message="获取成功",
        data=records
    )


@router.get("/{package_id}/statistics", response_model=SuccessResponse[DetailedStatisticsResponse])
async def get_package_statistics(
    package_id: int,
    period: str = Query("7d", regex="^(1d|7d|30d)$", description="统计周期"),
    current_user: TokenData = Depends(get_current_user),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """
    获取包裹统计分析
    
    - **package_id**: 包裹ID
    - **period**: 统计周期 (1d, 7d, 30d)
    """
    statistics = monitor_service.get_package_statistics(
        current_user.user_id, package_id, period
    )
    return SuccessResponse(
        message="获取成功",
        data=statistics
    )


@router.get("/{package_id}/export")
async def export_package_data(
    package_id: int,
    format: str = Query("csv", regex="^csv$", description="导出格式"),
    current_user: TokenData = Depends(get_current_user),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """
    导出包裹数据
    
    - **package_id**: 包裹ID
    - **format**: 导出格式 (目前只支持csv)
    """
    return monitor_service.export_package_data(current_user.user_id, package_id, format)
