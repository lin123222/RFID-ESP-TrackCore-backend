from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository, UserPackageRepository
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserUpdateRequest, 
    PasswordChangeRequest, UserResponse, LoginResponse, 
    PackageBindRequest, UserPackageResponse, PackageListResponse
)
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_token_expires_in


class UserService:
    """用户业务逻辑层"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.package_repo = UserPackageRepository(db)
    
    def register_user(self, user_data: UserRegisterRequest) -> UserResponse:
        """用户注册"""
        # 检查用户名是否已存在
        if self.user_repo.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 检查邮箱是否已存在
        if user_data.email and self.user_repo.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 创建用户
        password_hash = get_password_hash(user_data.password)
        db_user = self.user_repo.create_user(user_data, password_hash)
        
        return UserResponse.model_validate(db_user)
    
    def login_user(self, login_data: UserLoginRequest) -> LoginResponse:
        """用户登录"""
        # 获取用户
        db_user = self.user_repo.get_user_by_username(login_data.username)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # 验证密码
        if not verify_password(login_data.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # 检查用户状态
        if not db_user.is_active or db_user.status != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        # 创建访问令牌
        token_data = {"user_id": db_user.id, "username": db_user.username}
        access_token = create_access_token(data=token_data)
        
        return LoginResponse(
            user_id=db_user.id,
            username=db_user.username,
            token=access_token,
            expires_in=get_token_expires_in()
        )
    
    def get_user_info(self, user_id: int) -> UserResponse:
        """获取用户信息"""
        db_user = self.user_repo.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(db_user)
    
    def update_user_info(self, user_id: int, user_data: UserUpdateRequest) -> UserResponse:
        """更新用户信息"""
        # 检查邮箱是否已被其他用户使用
        if user_data.email:
            existing_user = self.user_repo.get_user_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered by another user"
                )
        
        db_user = self.user_repo.update_user(user_id, user_data)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(db_user)
    
    def change_password(self, user_id: int, password_data: PasswordChangeRequest) -> bool:
        """修改密码"""
        db_user = self.user_repo.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 验证旧密码
        if not verify_password(password_data.old_password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        # 更新密码
        new_password_hash = get_password_hash(password_data.new_password)
        return self.user_repo.update_password(user_id, new_password_hash)


class PackageService:
    """包裹业务逻辑层"""
    
    def __init__(self, db: Session):
        self.db = db
        self.package_repo = UserPackageRepository(db)
    
    def bind_package(self, user_id: int, package_data: PackageBindRequest) -> UserPackageResponse:
        """绑定包裹"""
        # 检查包裹是否已被绑定
        existing_package = self.package_repo.get_user_package(user_id, package_data.package_id)
        if existing_package:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Package already bound to this user"
            )
        
        # 绑定包裹
        db_user_package = self.package_repo.bind_package(user_id, package_data)
        
        # 获取包裹统计信息
        latest_record = self.package_repo.get_package_latest_record(package_data.package_id)
        record_count = self.package_repo.get_package_record_count(package_data.package_id)
        
        # 构建响应
        response = UserPackageResponse.model_validate(db_user_package)
        response.record_count = record_count
        
        if latest_record:
            response.latest_temperature = latest_record.max_temperature
            response.latest_humidity = latest_record.avg_humidity
            response.last_update = latest_record.created_at
        
        return response
    
    def unbind_package(self, user_id: int, package_id: int) -> bool:
        """解绑包裹"""
        success = self.package_repo.unbind_package(user_id, package_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or not bound to this user"
            )
        return success
    
    def get_user_packages(self, user_id: int, page: int = 1, size: int = 10) -> PackageListResponse:
        """获取用户包裹列表"""
        skip = (page - 1) * size
        
        # 获取包裹列表
        packages = self.package_repo.get_user_packages(user_id, skip, size)
        total = self.package_repo.get_user_package_count(user_id)
        
        # 构建响应列表
        items = []
        for package in packages:
            # 获取包裹统计信息
            latest_record = self.package_repo.get_package_latest_record(package.package_id)
            record_count = self.package_repo.get_package_record_count(package.package_id)
            
            response = UserPackageResponse.model_validate(package)
            response.record_count = record_count
            
            if latest_record:
                response.latest_temperature = latest_record.max_temperature
                response.latest_humidity = latest_record.avg_humidity
                response.last_update = latest_record.created_at
            
            items.append(response)
        
        return PackageListResponse(
            total=total,
            page=page,
            size=size,
            items=items
        )
    
    def get_package_detail(self, user_id: int, package_id: int) -> UserPackageResponse:
        """获取包裹详情"""
        # 检查包裹所有权
        if not self.package_repo.check_package_ownership(user_id, package_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        # 获取包裹信息
        db_user_package = self.package_repo.get_user_package(user_id, package_id)
        if not db_user_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found"
            )
        
        # 获取包裹统计信息
        latest_record = self.package_repo.get_package_latest_record(package_id)
        record_count = self.package_repo.get_package_record_count(package_id)
        
        # 构建响应
        response = UserPackageResponse.model_validate(db_user_package)
        response.record_count = record_count
        
        if latest_record:
            response.latest_temperature = latest_record.max_temperature
            response.latest_humidity = latest_record.avg_humidity
            response.last_update = latest_record.created_at
        
        return response
