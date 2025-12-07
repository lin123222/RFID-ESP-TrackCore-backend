"""
设备相关的数据验证模型
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class DeviceCreateRequest(BaseModel):
    """创建设备请求"""
    device_id: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="设备唯一标识（如：ESP32-001）",
        example="ESP32-001"
    )
    device_name: Optional[str] = Field(
        None, 
        max_length=100, 
        description="设备名称（可选）",
        example="仓库入口设备"
    )
    description: Optional[str] = Field(
        None, 
        description="设备描述（可选）",
        example="位于仓库入口的RFID读取设备"
    )


class DeviceResponse(BaseModel):
    """设备响应"""
    id: int = Field(..., description="设备主键ID")
    device_id: str = Field(..., description="设备唯一标识")
    device_name: Optional[str] = Field(None, description="设备名称")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    last_seen: Optional[datetime] = Field(None, description="最后活跃时间")
    secret_key: Optional[str] = Field(None, description="密钥（只在创建时返回一次）")
    
    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """设备列表响应"""
    total: int = Field(..., description="设备总数")
    devices: List[DeviceResponse] = Field(..., description="设备列表")

