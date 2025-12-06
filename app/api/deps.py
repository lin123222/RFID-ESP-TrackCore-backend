from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.package_repository import PackageRepository
from app.services.package_service import PackageService
from app.services.user import UserService, PackageService as UserPackageService
from app.utils.auth import verify_token
from app.schemas.user import TokenData


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
