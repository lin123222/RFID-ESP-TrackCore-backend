from fastapi import APIRouter, Depends, Query
from app.schemas.user import (
    PackageBindRequest, UserPackageResponse, PackageListResponse
)
from app.schemas.common import SuccessResponse
from app.services.user import PackageService
from app.api.deps import get_user_package_service, get_current_user
from app.schemas.user import TokenData

router = APIRouter()


@router.post("/bind", response_model=SuccessResponse[UserPackageResponse])
async def bind_package(
    package_data: PackageBindRequest,
    current_user: TokenData = Depends(get_current_user),
    package_service: PackageService = Depends(get_user_package_service)
):
    """
    绑定包裹
    
    - **package_id**: 包裹ID
    - **package_name**: 包裹名称 (可选)
    - **description**: 包裹描述 (可选)
    """
    package = package_service.bind_package(current_user.user_id, package_data)
    return SuccessResponse(
        message="包裹绑定成功",
        data=package
    )


@router.delete("/{package_id}", response_model=SuccessResponse[bool])
async def unbind_package(
    package_id: int,
    current_user: TokenData = Depends(get_current_user),
    package_service: PackageService = Depends(get_user_package_service)
):
    """
    解绑包裹
    
    - **package_id**: 包裹ID
    """
    success = package_service.unbind_package(current_user.user_id, package_id)
    return SuccessResponse(
        message="包裹解绑成功",
        data=success
    )


@router.get("", response_model=SuccessResponse[PackageListResponse])
async def get_user_packages(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: TokenData = Depends(get_current_user),
    package_service: PackageService = Depends(get_user_package_service)
):
    """
    获取用户包裹列表
    
    - **page**: 页码 (从1开始)
    - **size**: 每页数量 (1-100)
    """
    packages = package_service.get_user_packages(current_user.user_id, page, size)
    return SuccessResponse(
        message="获取成功",
        data=packages
    )


@router.get("/{package_id}", response_model=SuccessResponse[UserPackageResponse])
async def get_package_detail(
    package_id: int,
    current_user: TokenData = Depends(get_current_user),
    package_service: PackageService = Depends(get_user_package_service)
):
    """
    获取包裹详情
    
    - **package_id**: 包裹ID
    """
    package = package_service.get_package_detail(current_user.user_id, package_id)
    return SuccessResponse(
        message="获取成功",
        data=package
    )
