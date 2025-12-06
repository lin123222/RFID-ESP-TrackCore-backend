from sqlalchemy import Column, Integer, Float, BigInteger, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base


class PackageRecord(Base):
    """包裹环境监测记录模型"""
    
    __tablename__ = "package_records"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="记录ID")
    
    # 业务字段
    package_id = Column(Integer, nullable=False, index=True, comment="包裹ID")
    max_temperature = Column(Float, nullable=False, comment="最高温度(°C)")
    avg_humidity = Column(Float, nullable=False, comment="平均湿度(%)")
    over_threshold_time = Column(Integer, nullable=False, comment="超阈值时间(秒)")
    timestamp = Column(BigInteger, nullable=False, comment="Unix时间戳")
    
    # 系统字段
    created_at = Column(
        DateTime, 
        server_default=func.now(), 
        nullable=False,
        comment="记录创建时间"
    )
    
    # 创建复合索引（用于查询优化）
    __table_args__ = (
        Index('idx_package_timestamp', 'package_id', 'timestamp'),
        {'comment': '包裹环境监测记录表'}
    )
    
    def __repr__(self):
        return (
            f"<PackageRecord(id={self.id}, package_id={self.package_id}, "
            f"max_temperature={self.max_temperature}, avg_humidity={self.avg_humidity}, "
            f"over_threshold_time={self.over_threshold_time}, timestamp={self.timestamp})>"
        )
