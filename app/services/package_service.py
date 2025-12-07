from typing import Dict, Any, List
from loguru import logger
from app.repositories.package_repository import PackageRepository
from app.schemas.package import (
    PackageUploadRequest, 
    PackageRecordResponse,
    PackageHistoryResponse
)
from app.core.config import settings


class PackageService:
    """包裹业务逻辑层"""
    
    def __init__(self, repository: PackageRepository):
        self.repository = repository
    
    def save_package_data(self, data: PackageUploadRequest) -> Dict[str, Any]:
        """
        保存包裹数据
        
        Args:
            data: 包裹上传数据
            
        Returns:
            保存结果
        """
        # 业务逻辑：温度异常检测
        self._check_temperature_alert(data.package_id, data.max_temperature)
        
        # 保存数据
        try:
            record = self.repository.create(data)
            logger.info(
                f"Package data saved - ID: {data.package_id}, "
                f"MaxTemp: {data.max_temperature}°C, AvgHumidity: {data.avg_humidity}%, "
                f"OverTime: {data.over_threshold_time}s, Timestamp: {data.timestamp}"
            )
            
            return {
                "status": "success",
                "message": f"Data for package {data.package_id} received",
                "record_id": record.id
            }
        except Exception as e:
            logger.error(f"Failed to save package data: {str(e)}")
            raise
    
    def get_package_history(
        self, 
        package_id: int, 
        limit: int = 100,
        offset: int = 0
    ) -> PackageHistoryResponse:
        """
        获取包裹历史记录
        
        Args:
            package_id: 包裹ID
            limit: 返回记录数量限制
            offset: 偏移量
            
        Returns:
            包裹历史记录
        """
        records = self.repository.get_by_package_id(package_id, limit, offset)
        total = self.repository.count_by_package_id(package_id)
        
        return PackageHistoryResponse(
            package_id=package_id,
            total=total,
            records=[PackageRecordResponse.model_validate(r) for r in records]
        )
    
    
    def _check_temperature_alert(self, package_id: int, temperature: float) -> None:
        """
        检查温度是否异常
        
        Args:
            package_id: 包裹ID
            temperature: 温度值
        """
        if temperature > settings.TEMP_HIGH_THRESHOLD:
            logger.warning(
                f"⚠️ HIGH TEMPERATURE ALERT - Package {package_id}: "
                f"{temperature}°C (Threshold: {settings.TEMP_HIGH_THRESHOLD}°C)"
            )
            # TODO: 可以在这里添加告警通知逻辑（邮件、短信等）
        
        elif temperature < settings.TEMP_LOW_THRESHOLD:
            logger.warning(
                f"⚠️ LOW TEMPERATURE ALERT - Package {package_id}: "
                f"{temperature}°C (Threshold: {settings.TEMP_LOW_THRESHOLD}°C)"
            )
            # TODO: 可以在这里添加告警通知逻辑
