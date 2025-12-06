from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# 当前数据响应
class CurrentDataResponse(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: Optional[datetime] = None


# 日期范围响应
class DateRangeResponse(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None


# 包裹统计响应
class PackageStatisticsResponse(BaseModel):
    total_records: int
    avg_temperature: Optional[float] = None
    avg_humidity: Optional[float] = None
    date_range: Optional[DateRangeResponse] = None


# 包裹详情响应
class PackageDetailResponse(BaseModel):
    package_id: int
    package_name: Optional[str] = None
    description: Optional[str] = None
    current_data: Optional[CurrentDataResponse] = None
    statistics: Optional[PackageStatisticsResponse] = None

    class Config:
        from_attributes = True


# 包裹记录响应
class PackageRecordResponse(BaseModel):
    id: int
    max_temperature: float
    avg_humidity: float
    over_threshold_time: int
    timestamp: int
    created_at: datetime

    class Config:
        from_attributes = True


# 包裹记录列表响应
class PackageRecordsResponse(BaseModel):
    total: int
    page: int
    size: int
    records: List[PackageRecordResponse]


# 数据统计请求参数
class StatisticsPeriod(BaseModel):
    period: str = Field("7d", description="统计周期: 1d, 7d, 30d")


# 温湿度统计
class TemperatureHumidityStats(BaseModel):
    avg: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None


# 每日统计
class DailyStats(BaseModel):
    date: str
    avg_temp: Optional[float] = None
    avg_humidity: Optional[float] = None
    record_count: int


# 详细统计响应
class DetailedStatisticsResponse(BaseModel):
    period: str
    total_records: int
    temperature: TemperatureHumidityStats
    humidity: TemperatureHumidityStats
    daily_stats: List[DailyStats]


# 导出请求参数
class ExportFormat(BaseModel):
    format: str = Field("csv", description="导出格式: csv")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
