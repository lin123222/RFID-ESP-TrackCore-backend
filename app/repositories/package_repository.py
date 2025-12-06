from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.package import PackageRecord
from app.schemas.package import PackageUploadRequest


class PackageRepository:
    """包裹数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: PackageUploadRequest) -> PackageRecord:
        """
        创建新的包裹记录
        
        Args:
            data: 包裹上传数据
            
        Returns:
            创建的记录对象
        """
        db_record = PackageRecord(
            package_id=data.package_id,
            max_temperature=data.max_temperature,
            avg_humidity=data.avg_humidity,
            over_threshold_time=data.over_threshold_time,
            timestamp=data.timestamp
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record
    
    def get_by_id(self, record_id: int) -> Optional[PackageRecord]:
        """
        根据记录ID获取单条记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            记录对象或 None
        """
        return self.db.query(PackageRecord).filter(
            PackageRecord.id == record_id
        ).first()
    
    def get_by_package_id(
        self, 
        package_id: int, 
        limit: int = 100,
        offset: int = 0
    ) -> List[PackageRecord]:
        """
        根据包裹ID获取历史记录
        
        Args:
            package_id: 包裹ID
            limit: 返回记录数量限制
            offset: 偏移量
            
        Returns:
            记录列表
        """
        return self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        ).order_by(
            desc(PackageRecord.timestamp)
        ).limit(limit).offset(offset).all()
    
    def count_by_package_id(self, package_id: int) -> int:
        """
        统计指定包裹的记录数量
        
        Args:
            package_id: 包裹ID
            
        Returns:
            记录数量
        """
        return self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        ).count()
    
    def get_latest_by_package_id(self, package_id: int) -> Optional[PackageRecord]:
        """
        获取指定包裹的最新记录
        
        Args:
            package_id: 包裹ID
            
        Returns:
            最新记录或 None
        """
        return self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        ).order_by(
            desc(PackageRecord.timestamp)
        ).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[PackageRecord]:
        """
        获取所有记录（分页）
        
        Args:
            limit: 返回记录数量限制
            offset: 偏移量
            
        Returns:
            记录列表
        """
        return self.db.query(PackageRecord).order_by(
            desc(PackageRecord.created_at)
        ).limit(limit).offset(offset).all()
    
    def delete_by_id(self, record_id: int) -> bool:
        """
        删除指定记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        record = self.get_by_id(record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return True
        return False
