from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# 用户注册请求
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")


# 用户登录请求
class UserLoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# 用户信息更新请求
class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = Field(None, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")


# 密码修改请求
class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


# 用户响应
class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    status: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 登录响应
class LoginResponse(BaseModel):
    user_id: int
    username: str
    token: str
    expires_in: int
    token_type: str = "bearer"


# Token数据
class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


# 包裹绑定请求
class PackageBindRequest(BaseModel):
    package_id: int = Field(..., description="包裹ID")
    package_name: Optional[str] = Field(None, max_length=100, description="包裹名称")
    description: Optional[str] = Field(None, max_length=500, description="包裹描述")


# 用户包裹响应
class UserPackageResponse(BaseModel):
    id: int
    package_id: int
    package_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # 包裹统计信息
    latest_temperature: Optional[float] = None
    latest_humidity: Optional[float] = None
    last_update: Optional[datetime] = None
    record_count: int = 0

    class Config:
        from_attributes = True


# 包裹列表响应
class PackageListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserPackageResponse]
