"""
设备模型
用于管理 ESP32 设备
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Device(Base):
    """ESP32 设备模型"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True, comment="设备ID")
    device_id = Column(String(50), unique=True, nullable=False, index=True, comment="设备唯一标识")
    device_name = Column(String(100), nullable=True, comment="设备名称")
    secret_key = Column(String(64), nullable=False, comment="HMAC密钥（用于签名）")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    description = Column(Text, nullable=True, comment="设备描述")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    last_seen = Column(DateTime, nullable=True, comment="最后活跃时间")
    
    def __repr__(self):
        return f"<Device(device_id='{self.device_id}', name='{self.device_name}')>"

