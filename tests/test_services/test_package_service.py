"""
包裹服务层测试
"""
import pytest
from datetime import datetime
from app.services.package_service import PackageService
from app.repositories.package_repository import PackageRepository
from app.schemas.package import PackageUploadRequest


class TestPackageService:
    """包裹服务层测试类"""
    
    @pytest.fixture
    def service(self, db_session):
        """创建服务实例"""
        repository = PackageRepository(db_session)
        return PackageService(repository)
    
    def test_save_package_data(self, service):
        """测试保存包裹数据"""
        data = PackageUploadRequest(
            package_id=1001,
            temperature=24.5,
            timestamp=int(datetime.now().timestamp())
        )
        
        result = service.save_package_data(data)
        
        assert result["status"] == "success"
        assert "record_id" in result
        assert result["message"] == "Data for package 1001 received"
    
    def test_get_package_history(self, service):
        """测试获取包裹历史"""
        package_id = 1001
        
        # 保存几条数据
        for i in range(3):
            data = PackageUploadRequest(
                package_id=package_id,
                temperature=20.0 + i,
                timestamp=int(datetime.now().timestamp()) - i * 3600
            )
            service.save_package_data(data)
        
        # 获取历史
        history = service.get_package_history(package_id)
        
        assert history.package_id == package_id
        assert history.total_records == 3
        assert len(history.records) == 3
    
    def test_get_latest_record(self, service):
        """测试获取最新记录"""
        package_id = 1002
        
        # 保存数据
        timestamps = []
        for i in range(3):
            ts = int(datetime.now().timestamp()) - i * 3600
            timestamps.append(ts)
            data = PackageUploadRequest(
                package_id=package_id,
                temperature=20.0 + i,
                timestamp=ts
            )
            service.save_package_data(data)
        
        # 获取最新记录
        latest = service.get_latest_record(package_id)
        
        assert latest is not None
        assert latest.package_id == package_id
        assert latest.timestamp == max(timestamps)
    
    def test_get_latest_record_not_found(self, service):
        """测试获取不存在的记录"""
        latest = service.get_latest_record(9999)
        assert latest is None
