"""
设备管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.core.database import get_db
from app.api.deps import get_current_user, get_device_repository
from app.repositories.device_repository import DeviceRepository
from app.utils.security import generate_secret_key
from app.schemas.device import (
    DeviceCreateRequest,
    DeviceResponse,
    DeviceListResponse
)
from app.schemas.user import TokenData

router = APIRouter()


@router.post("/devices", response_model=DeviceResponse, tags=["Device"])
async def create_device(
    device_data: DeviceCreateRequest,
    current_user: TokenData = Depends(get_current_user),  # 需要登录
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """
    注册新设备（需要登录）
    
    自动生成 secret_key，只在创建时返回一次，请妥善保管
    """
    # 检查设备是否已存在
    existing = device_repo.get_by_device_id(device_data.device_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device {device_data.device_id} already exists"
        )
    
    # 生成密钥
    secret_key = generate_secret_key()
    
    # 创建设备
    device = device_repo.create(
        device_id=device_data.device_id,
        device_name=device_data.device_name,
        secret_key=secret_key,
        description=device_data.description
    )
    
    logger.info(f"Device created by user {current_user.username}: {device.device_id}")
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        is_active=device.is_active,
        created_at=device.created_at,
        last_seen=device.last_seen,
        secret_key=secret_key  # 只在创建时返回一次
    )


@router.get("/devices", response_model=DeviceListResponse, tags=["Device"])
async def list_devices(
    skip: int = Query(default=0, ge=0, description="偏移量"),
    limit: int = Query(default=100, ge=1, le=1000, description="返回数量"),
    current_user: TokenData = Depends(get_current_user),  # 需要登录
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """
    获取设备列表（需要登录）
    """
    devices = device_repo.get_all(skip=skip, limit=limit)
    total = device_repo.count_all()
    
    return DeviceListResponse(
        total=total,
        devices=[
            DeviceResponse(
                id=d.id,
                device_id=d.device_id,
                device_name=d.device_name,
                is_active=d.is_active,
                created_at=d.created_at,
                last_seen=d.last_seen,
                secret_key=None  # 列表不返回密钥
            )
            for d in devices
        ]
    )


@router.get("/devices/{device_id}", response_model=DeviceResponse, tags=["Device"])
async def get_device(
    device_id: str,
    current_user: TokenData = Depends(get_current_user),  # 需要登录
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """
    获取设备详情（需要登录）
    """
    device = device_repo.get_by_device_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        is_active=device.is_active,
        created_at=device.created_at,
        last_seen=device.last_seen,
        secret_key=None  # 详情不返回密钥
    )


@router.post("/devices/{device_id}/activate", tags=["Device"])
async def activate_device(
    device_id: str,
    current_user: TokenData = Depends(get_current_user),  # 需要登录
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """
    激活设备（需要登录）
    """
    if device_repo.activate(device_id):
        logger.info(f"Device {device_id} activated by user {current_user.username}")
        return {"status": "success", "message": f"Device {device_id} activated"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Device not found"
    )


@router.post("/devices/{device_id}/deactivate", tags=["Device"])
async def deactivate_device(
    device_id: str,
    current_user: TokenData = Depends(get_current_user),  # 需要登录
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """
    停用设备（需要登录）
    """
    if device_repo.deactivate(device_id):
        logger.info(f"Device {device_id} deactivated by user {current_user.username}")
        return {"status": "success", "message": f"Device {device_id} deactivated"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Device not found"
    )

