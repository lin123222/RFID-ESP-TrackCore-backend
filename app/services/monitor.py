import csv
import io
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.repositories.monitor import MonitorRepository
from app.schemas.monitor import (
    PackageDetailResponse, CurrentDataResponse, PackageStatisticsResponse,
    DateRangeResponse, PackageRecordsResponse, PackageRecordResponse,
    DetailedStatisticsResponse, TemperatureHumidityStats, DailyStats
)


class MonitorService:
    """数据监控业务逻辑层"""
    
    def __init__(self, db: Session):
        self.db = db
        self.monitor_repo = MonitorRepository(db)
    
    def get_package_detail(self, user_id: int, package_id: int) -> PackageDetailResponse:
        """获取包裹详情"""
        # 检查包裹所有权
        if not self.monitor_repo.check_package_ownership(user_id, package_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        # 获取最新记录
        latest_record = self.monitor_repo.get_package_latest_record(package_id)
        
        # 获取统计信息
        stats = self.monitor_repo.get_package_statistics(package_id)
        
        # 构建当前数据响应
        current_data = None
        if latest_record:
            current_data = CurrentDataResponse(
                temperature=latest_record.max_temperature,
                humidity=latest_record.avg_humidity,
                timestamp=latest_record.created_at
            )
        
        # 构建统计响应
        statistics = PackageStatisticsResponse(
            total_records=stats['total_records'],
            avg_temperature=stats['avg_temperature'],
            avg_humidity=stats['avg_humidity']
        )
        
        # 添加日期范围
        if stats['start_timestamp'] and stats['end_timestamp']:
            statistics.date_range = DateRangeResponse(
                start=datetime.fromtimestamp(stats['start_timestamp']),
                end=datetime.fromtimestamp(stats['end_timestamp'])
            )
        
        return PackageDetailResponse(
            package_id=package_id,
            current_data=current_data,
            statistics=statistics
        )
    
    def get_package_records(
        self, 
        user_id: int, 
        package_id: int, 
        page: int = 1, 
        size: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PackageRecordsResponse:
        """获取包裹历史记录"""
        # 检查包裹所有权
        if not self.monitor_repo.check_package_ownership(user_id, package_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        skip = (page - 1) * size
        records, total = self.monitor_repo.get_package_records(
            package_id, skip, size, start_date, end_date
        )
        
        # 转换为响应格式
        record_responses = [
            PackageRecordResponse.model_validate(record) for record in records
        ]
        
        return PackageRecordsResponse(
            total=total,
            page=page,
            size=size,
            records=record_responses
        )
    
    def get_package_statistics(
        self, 
        user_id: int, 
        package_id: int, 
        period: str = "7d"
    ) -> DetailedStatisticsResponse:
        """获取包裹统计分析"""
        # 检查包裹所有权
        if not self.monitor_repo.check_package_ownership(user_id, package_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        # 解析周期
        period_days = {
            "1d": 1,
            "7d": 7,
            "30d": 30
        }
        
        days = period_days.get(period, 7)
        
        # 获取统计数据
        stats = self.monitor_repo.get_package_statistics(package_id, days)
        daily_stats = self.monitor_repo.get_daily_statistics(package_id, days)
        
        # 构建响应
        temperature_stats = TemperatureHumidityStats(
            avg=stats['avg_temperature'],
            min=stats['min_temperature'],
            max=stats['max_temperature']
        )
        
        humidity_stats = TemperatureHumidityStats(
            avg=stats['avg_humidity'],
            min=stats['min_humidity'],
            max=stats['max_humidity']
        )
        
        daily_stats_responses = [
            DailyStats(**daily_stat) for daily_stat in daily_stats
        ]
        
        return DetailedStatisticsResponse(
            period=period,
            total_records=stats['total_records'],
            temperature=temperature_stats,
            humidity=humidity_stats,
            daily_stats=daily_stats_responses
        )
    
    def export_package_data(self, user_id: int, package_id: int, format: str = "csv") -> StreamingResponse:
        """导出包裹数据"""
        # 检查包裹所有权
        if not self.monitor_repo.check_package_ownership(user_id, package_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        if format != "csv":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV format is supported"
            )
        
        # 获取所有记录
        records = self.monitor_repo.get_all_package_records(package_id)
        
        # 生成CSV内容
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            'ID', 'Package ID', 'Max Temperature (°C)', 'Avg Humidity (%)', 
            'Over Threshold Time (s)', 'Timestamp', 'Created At'
        ])
        
        # 写入数据
        for record in records:
            writer.writerow([
                record.id,
                record.package_id,
                record.max_temperature,
                record.avg_humidity,
                record.over_threshold_time,
                record.timestamp,
                record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # 准备响应
        output.seek(0)
        
        def iter_csv():
            yield output.getvalue()
        
        filename = f"package_{package_id}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
