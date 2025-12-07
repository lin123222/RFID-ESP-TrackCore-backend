from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger
from app.core.database import get_db
from app.repositories.package_repository import PackageRepository
from app.repositories.device_repository import DeviceRepository
from app.services.package_service import PackageService
from app.services.user import UserService, PackageService as UserPackageService
from app.utils.auth import verify_token
from app.utils.security import build_signature_data, verify_hmac_signature
from app.schemas.user import TokenData
from app.schemas.package import PackageUploadRequest
from app.models.device import Device


def get_package_repository(db: Session = None) -> PackageRepository:
    """
    获取包裹数据访问层实例
    
    Args:
        db: 数据库会话
        
    Returns:
        PackageRepository 实例
    """
    if db is None:
        db = next(get_db())
    return PackageRepository(db)


def get_package_service(db: Session = None) -> PackageService:
    """
    获取包裹业务逻辑层实例
    
    Args:
        db: 数据库会话
        
    Returns:
        PackageService 实例
    """
    repository = get_package_repository(db)
    return PackageService(repository)


# JWT认证
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    获取当前用户信息
    
    Args:
        credentials: JWT凭证
        
    Returns:
        TokenData: 用户令牌数据
    """
    token_data = verify_token(credentials.credentials)
    return TokenData(**token_data)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    获取用户业务逻辑层实例
    
    Args:
        db: 数据库会话
        
    Returns:
        UserService 实例
    """
    return UserService(db)


def get_user_package_service(db: Session = Depends(get_db)) -> UserPackageService:
    """
    获取用户包裹业务逻辑层实例
    
    Args:
        db: 数据库会话
        
    Returns:
        UserPackageService 实例
    """
    return UserPackageService(db)


def get_device_repository(db: Session = Depends(get_db)) -> DeviceRepository:
    """
    获取设备仓库实例
    
    Args:
        db: 数据库会话
        
    Returns:
        DeviceRepository 实例
    """
    return DeviceRepository(db)


async def verify_device_authentication(
    request: Request,
    payload: PackageUploadRequest,
    x_device_id: Optional[str] = Header(None, alias="X-Device-ID"),
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    x_timestamp: Optional[int] = Header(None, alias="X-Timestamp"),
    device_repo: DeviceRepository = Depends(get_device_repository)
) -> Device:
    """
    验证设备身份和签名
    
    验证流程：
    1. 检查请求头是否包含必要字段
    2. 通过 device_id 查找设备
    3. 检查设备是否激活
    4. 构建签名字符串
    5. 验证 HMAC 签名
    6. 验证时间戳（防重放）
    7. 更新设备最后活跃时间
    
    Args:
        request: FastAPI 请求对象
        payload: 请求体数据
        x_device_id: 设备ID（请求头）
        x_signature: HMAC签名（请求头）
        x_timestamp: 时间戳（请求头）
        device_repo: 设备仓库
        
    Returns:
        验证通过的设备对象
        
    Raises:
        HTTPException: 验证失败时抛出
    """
    # 1. 检查请求头
    if not x_device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Device-ID header"
        )
    
    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Signature header"
        )
    
    if not x_timestamp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Timestamp header"
        )
    
    # 2. 查找设备
    device = device_repo.get_by_device_id(x_device_id)
    if not device:
        logger.warning(f"Unknown device attempted access: {x_device_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device ID"
        )
    
    # 3. 检查设备状态
    if not device.is_active:
        logger.warning(f"Inactive device attempted access: {x_device_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device is not active"
        )
    
    # 4. 构建签名字符串
    sign_data = build_signature_data(
        package_id=payload.package_id,
        max_temperature=payload.max_temperature,
        avg_humidity=payload.avg_humidity,
        over_threshold_time=payload.over_threshold_time,
        timestamp=payload.timestamp
    )
    
    # 5. 验证签名
    if not verify_hmac_signature(sign_data, x_signature, device.secret_key):
        logger.warning(f"Invalid signature from device: {x_device_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # 6. 验证时间戳（防重放攻击）
    current_timestamp = int(datetime.now().timestamp())
    time_diff = abs(current_timestamp - x_timestamp)
    
    # 允许 5 分钟的时间误差
    if time_diff > 300:  # 5分钟 = 300秒
        logger.warning(
            f"Timestamp out of range from device {x_device_id}: "
            f"diff={time_diff}s"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Timestamp out of range (diff: {time_diff}s)"
        )
    
    # 7. 更新最后活跃时间
    device_repo.update_last_seen(x_device_id)
    
    logger.info(f"Device authenticated: {x_device_id}")
    return device
