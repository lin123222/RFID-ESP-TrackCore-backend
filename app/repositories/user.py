from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.models.user import User, UserPackage
from app.models.package import PackageRecord
from app.schemas.user import UserRegisterRequest, UserUpdateRequest, PackageBindRequest


class UserRepository:
    """用户数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserRegisterRequest, password_hash: str) -> User:
        """创建用户"""
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, user_data: UserUpdateRequest) -> Optional[User]:
        """更新用户信息"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """更新用户密码"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        db_user.password_hash = new_password_hash
        self.db.commit()
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """停用用户"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.commit()
        return True


class UserPackageRepository:
    """用户包裹关联数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def bind_package(self, user_id: int, package_data: PackageBindRequest) -> UserPackage:
        """绑定包裹"""
        db_user_package = UserPackage(
            user_id=user_id,
            package_id=package_data.package_id,
            package_name=package_data.package_name,
            description=package_data.description
        )
        self.db.add(db_user_package)
        self.db.commit()
        self.db.refresh(db_user_package)
        return db_user_package
    
    def unbind_package(self, user_id: int, package_id: int) -> bool:
        """解绑包裹"""
        db_user_package = self.db.query(UserPackage).filter(
            and_(
                UserPackage.user_id == user_id,
                UserPackage.package_id == package_id
            )
        ).first()
        
        if not db_user_package:
            return False
        
        self.db.delete(db_user_package)
        self.db.commit()
        return True
    
    def get_user_packages(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserPackage]:
        """获取用户包裹列表"""
        return self.db.query(UserPackage).filter(
            and_(
                UserPackage.user_id == user_id,
                UserPackage.is_active == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_user_package_count(self, user_id: int) -> int:
        """获取用户包裹总数"""
        return self.db.query(UserPackage).filter(
            and_(
                UserPackage.user_id == user_id,
                UserPackage.is_active == True
            )
        ).count()
    
    def get_user_package(self, user_id: int, package_id: int) -> Optional[UserPackage]:
        """获取用户特定包裹"""
        return self.db.query(UserPackage).filter(
            and_(
                UserPackage.user_id == user_id,
                UserPackage.package_id == package_id,
                UserPackage.is_active == True
            )
        ).first()
    
    def check_package_ownership(self, user_id: int, package_id: int) -> bool:
        """检查包裹所有权"""
        return self.db.query(UserPackage).filter(
            and_(
                UserPackage.user_id == user_id,
                UserPackage.package_id == package_id,
                UserPackage.is_active == True
            )
        ).first() is not None
    
    def get_package_latest_record(self, package_id: int) -> Optional[PackageRecord]:
        """获取包裹最新记录"""
        return self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        ).order_by(desc(PackageRecord.timestamp)).first()
    
    def get_package_record_count(self, package_id: int) -> int:
        """获取包裹记录总数"""
        return self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        ).count()
