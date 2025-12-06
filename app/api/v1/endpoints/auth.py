from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserUpdateRequest, 
    PasswordChangeRequest, UserResponse, LoginResponse
)
from app.schemas.common import SuccessResponse
from app.services.user import UserService
from app.api.deps import get_user_service, get_current_user
from app.schemas.user import TokenData

router = APIRouter()


@router.post("/register", response_model=SuccessResponse[UserResponse])
async def register_user(
    user_data: UserRegisterRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    用户注册
    
    - **username**: 用户名 (3-50字符)
    - **email**: 邮箱 (可选)
    - **password**: 密码 (6-50字符)
    - **nickname**: 昵称 (可选)
    """
    user = user_service.register_user(user_data)
    return SuccessResponse(
        message="注册成功",
        data=user
    )


@router.post("/login", response_model=SuccessResponse[LoginResponse])
async def login_user(
    login_data: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    """
    login_result = user_service.login_user(login_data)
    return SuccessResponse(
        message="登录成功",
        data=login_result
    )


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取当前用户信息
    """
    user = user_service.get_user_info(current_user.user_id)
    return SuccessResponse(
        message="获取成功",
        data=user
    )


@router.put("/me", response_model=SuccessResponse[UserResponse])
async def update_current_user(
    user_data: UserUpdateRequest,
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    更新当前用户信息
    
    - **email**: 邮箱 (可选)
    - **nickname**: 昵称 (可选)
    """
    user = user_service.update_user_info(current_user.user_id, user_data)
    return SuccessResponse(
        message="更新成功",
        data=user
    )


@router.post("/change-password", response_model=SuccessResponse[bool])
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码 (6-50字符)
    """
    success = user_service.change_password(current_user.user_id, password_data)
    return SuccessResponse(
        message="密码修改成功",
        data=success
    )
