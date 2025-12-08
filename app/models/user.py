from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用户ID")
    
    # 基础信息
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), nullable=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 状态字段
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    
    # 系统字段
    created_at = Column(
        DateTime, 
        server_default=func.now(), 
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    # 创建索引
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
        {'comment': '用户表'}
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserPackage(Base):
    """用户包裹关联模型"""
    
    __tablename__ = "user_packages"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="关联ID")
    
    # 关联字段
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    package_id = Column(Integer, nullable=False, index=True, comment="包裹ID")
    
    # 包裹信息
    package_name = Column(String(100), nullable=True, comment="包裹名称")
    description = Column(String(500), nullable=True, comment="包裹描述")
    
    # 状态字段
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    
    # 系统字段
    created_at = Column(
        DateTime, 
        server_default=func.now(), 
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    # 创建索引和约束
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_package_id', 'package_id'),
        Index('uk_user_package', 'user_id', 'package_id', unique=True),
        {'comment': '用户包裹关联表'}
    )
    
    def __repr__(self):
        return (
            f"<UserPackage(id={self.id}, user_id={self.user_id}, "
            f"package_id={self.package_id}, package_name='{self.package_name}')>"
        )
