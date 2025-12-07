"""
设备数据访问层
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.device import Device


class DeviceRepository:
    """设备数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """
        根据 device_id 获取设备
        
        Args:
            device_id: 设备唯一标识
            
        Returns:
            设备对象或 None
        """
        return self.db.query(Device).filter(
            Device.device_id == device_id
        ).first()
    
    def create(
        self, 
        device_id: str, 
        device_name: str = None, 
        secret_key: str = None, 
        description: str = None
    ) -> Device:
        """
        创建设备
        
        Args:
            device_id: 设备唯一标识
            device_name: 设备名称（可选）
            secret_key: 密钥（如果为None，需要外部生成）
            description: 设备描述（可选）
            
        Returns:
            创建的设备对象
        """
        device = Device(
            device_id=device_id,
            device_name=device_name,
            secret_key=secret_key,
            description=description
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device
    
    def update_last_seen(self, device_id: str) -> bool:
        """
        更新设备最后活跃时间
        
        Args:
            device_id: 设备唯一标识
            
        Returns:
            是否更新成功
        """
        device = self.get_by_device_id(device_id)
        if device:
            device.last_seen = datetime.now()
            self.db.commit()
            return True
        return False
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Device]:
        """
        获取所有设备（分页）
        
        Args:
            skip: 偏移量
            limit: 返回数量限制
            
        Returns:
            设备列表
        """
        return self.db.query(Device).offset(skip).limit(limit).all()
    
    def count_all(self) -> int:
        """
        统计设备总数
        
        Returns:
            设备总数
        """
        return self.db.query(Device).count()
    
    def activate(self, device_id: str) -> bool:
        """
        激活设备
        
        Args:
            device_id: 设备唯一标识
            
        Returns:
            是否激活成功
        """
        device = self.get_by_device_id(device_id)
        if device:
            device.is_active = True
            self.db.commit()
            return True
        return False
    
    def deactivate(self, device_id: str) -> bool:
        """
        停用设备
        
        Args:
            device_id: 设备唯一标识
            
        Returns:
            是否停用成功
        """
        device = self.get_by_device_id(device_id)
        if device:
            device.is_active = False
            self.db.commit()
            return True
        return False
    
    def get_by_id(self, device_id: int) -> Optional[Device]:
        """
        根据主键ID获取设备
        
        Args:
            device_id: 主键ID
            
        Returns:
            设备对象或 None
        """
        return self.db.query(Device).filter(Device.id == device_id).first()

