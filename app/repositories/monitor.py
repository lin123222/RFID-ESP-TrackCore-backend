from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, text
from app.models.package import PackageRecord
from app.models.user import UserPackage


class MonitorRepository:
    """数据监控数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_package_records(
        self, 
        package_id: int, 
        skip: int = 0, 
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[PackageRecord], int]:
        """获取包裹记录列表和总数"""
        query = self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        )
        
        # 添加日期过滤
        if start_date:
            start_timestamp = int(start_date.timestamp())
            query = query.filter(PackageRecord.timestamp >= start_timestamp)
        
        if end_date:
            end_timestamp = int(end_date.timestamp())
            query = query.filter(PackageRecord.timestamp <= end_timestamp)
        
        # 获取总数
        total = query.count()
        
        # 获取记录列表
        records = query.order_by(desc(PackageRecord.timestamp)).offset(skip).limit(limit).all()
        
        return records, total
    
    def get_package_latest_record(self, package_id: int) -> Optional[PackageRecord]:
        """获取包裹最新记录"""
        return self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        ).order_by(desc(PackageRecord.timestamp)).first()
    
    def get_package_statistics(self, package_id: int, days: int = 7) -> dict:
        """获取包裹统计信息"""
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        # 查询统计数据
        stats = self.db.query(
            func.count(PackageRecord.id).label('total_records'),
            func.avg(PackageRecord.max_temperature).label('avg_temperature'),
            func.min(PackageRecord.max_temperature).label('min_temperature'),
            func.max(PackageRecord.max_temperature).label('max_temperature'),
            func.avg(PackageRecord.avg_humidity).label('avg_humidity'),
            func.min(PackageRecord.avg_humidity).label('min_humidity'),
            func.max(PackageRecord.avg_humidity).label('max_humidity'),
            func.min(PackageRecord.timestamp).label('min_timestamp'),
            func.max(PackageRecord.timestamp).label('max_timestamp')
        ).filter(
            and_(
                PackageRecord.package_id == package_id,
                PackageRecord.timestamp >= start_timestamp,
                PackageRecord.timestamp <= end_timestamp
            )
        ).first()
        
        return {
            'total_records': stats.total_records or 0,
            'avg_temperature': float(stats.avg_temperature) if stats.avg_temperature else None,
            'min_temperature': float(stats.min_temperature) if stats.min_temperature else None,
            'max_temperature': float(stats.max_temperature) if stats.max_temperature else None,
            'avg_humidity': float(stats.avg_humidity) if stats.avg_humidity else None,
            'min_humidity': float(stats.min_humidity) if stats.min_humidity else None,
            'max_humidity': float(stats.max_humidity) if stats.max_humidity else None,
            'start_timestamp': stats.min_timestamp,
            'end_timestamp': stats.max_timestamp
        }
    
    def get_daily_statistics(self, package_id: int, days: int = 7) -> List[dict]:
        """获取每日统计数据"""
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        # 使用原生SQL查询每日统计
        sql = text("""
            SELECT 
                DATE(FROM_UNIXTIME(timestamp)) as date,
                AVG(max_temperature) as avg_temp,
                AVG(avg_humidity) as avg_humidity,
                COUNT(*) as record_count
            FROM package_records 
            WHERE package_id = :package_id 
                AND timestamp >= :start_timestamp 
                AND timestamp <= :end_timestamp
            GROUP BY DATE(FROM_UNIXTIME(timestamp))
            ORDER BY date DESC
        """)
        
        result = self.db.execute(sql, {
            'package_id': package_id,
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp
        })
        
        daily_stats = []
        for row in result:
            daily_stats.append({
                'date': row.date.strftime('%Y-%m-%d'),
                'avg_temp': float(row.avg_temp) if row.avg_temp else None,
                'avg_humidity': float(row.avg_humidity) if row.avg_humidity else None,
                'record_count': row.record_count
            })
        
        return daily_stats
    
    def get_all_package_records(self, package_id: int) -> List[PackageRecord]:
        """获取包裹所有记录（用于导出）"""
        return self.db.query(PackageRecord).filter(
            PackageRecord.package_id == package_id
        ).order_by(desc(PackageRecord.timestamp)).all()
    
    def check_package_ownership(self, user_id: int, package_id: int) -> bool:
        """检查包裹所有权"""
        return self.db.query(UserPackage).filter(
            and_(
                UserPackage.user_id == user_id,
                UserPackage.package_id == package_id,
                UserPackage.is_active == True
            )
        ).first() is not None
