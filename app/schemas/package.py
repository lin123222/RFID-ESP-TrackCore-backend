from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime


class PackageUploadRequest(BaseModel):
    """包裹环境监测数据上传请求模型"""
    
    package_id: int = Field(
        ..., 
        gt=0, 
        description="包裹ID，必须为正整数",
        example=1001
    )
    max_temperature: float = Field(
        ..., 
        ge=-50.0, 
        le=100.0, 
        description="最高温度(°C)，范围: -50 ~ 100",
        example=28.5
    )
    avg_humidity: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="平均湿度(%)，范围: 0 ~ 100",
        example=65.2
    )
    over_threshold_time: int = Field(
        ..., 
        ge=0, 
        description="超阈值时间(秒)，必须为非负整数",
        example=3600
    )
    timestamp: int = Field(
        ..., 
        gt=0, 
        description="Unix时间戳（秒）",
        example=1700000000
    )
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """验证时间戳是否合理（不能是未来时间）"""
        current_timestamp = int(datetime.now().timestamp())
        if v > current_timestamp + 3600:  # 允许1小时的时间误差
            raise ValueError("时间戳不能是未来时间")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "package_id": 1001,
                "max_temperature": 28.5,
                "avg_humidity": 65.2,
                "over_threshold_time": 3600,
                "timestamp": 1700000000
            }
        }


class PackageRecordResponse(BaseModel):
    """包裹记录响应模型"""
    
    id: int = Field(..., description="记录ID")
    package_id: int = Field(..., description="包裹ID")
    max_temperature: float = Field(..., description="最高温度(°C)")
    avg_humidity: float = Field(..., description="平均湿度(%)")
    over_threshold_time: int = Field(..., description="超阈值时间(秒)")
    timestamp: int = Field(..., description="Unix时间戳")
    created_at: datetime = Field(..., description="记录创建时间")
    
    class Config:
        from_attributes = True  # 允许从 ORM 模型创建


class PackageHistoryResponse(BaseModel):
    """包裹历史记录响应模型"""
    
    package_id: int = Field(..., description="包裹ID")
    total_records: int = Field(..., description="总记录数")
    records: List[PackageRecordResponse] = Field(..., description="记录列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "package_id": 1001,
                "total_records": 2,
                "records": [
                    {
                        "id": 1,
                        "package_id": 1001,
                        "max_temperature": 28.5,
                        "avg_humidity": 65.2,
                        "over_threshold_time": 3600,
                        "timestamp": 1700000000,
                        "created_at": "2024-11-26T14:30:00"
                    }
                ]
            }
        }
