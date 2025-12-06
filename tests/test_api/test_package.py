"""
包裹 API 测试
"""
import pytest
from datetime import datetime


class TestPackageAPI:
    """包裹 API 测试类"""
    
    def test_upload_package_data_success(self, client):
        """测试成功上传包裹数据"""
        payload = {
            "package_id": 1001,
            "temperature": 24.5,
            "timestamp": int(datetime.now().timestamp())
        }
        
        response = client.post("/api/v1/upload", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "record_id" in data
        assert data["message"] == "Data for package 1001 received"
    
    def test_upload_invalid_package_id(self, client):
        """测试无效的包裹ID"""
        payload = {
            "package_id": -1,  # 无效：负数
            "temperature": 24.5,
            "timestamp": int(datetime.now().timestamp())
        }
        
        response = client.post("/api/v1/upload", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_upload_invalid_temperature(self, client):
        """测试无效的温度值"""
        payload = {
            "package_id": 1001,
            "temperature": 150.0,  # 超出范围
            "timestamp": int(datetime.now().timestamp())
        }
        
        response = client.post("/api/v1/upload", json=payload)
        assert response.status_code == 422
    
    def test_upload_future_timestamp(self, client):
        """测试未来时间戳"""
        payload = {
            "package_id": 1001,
            "temperature": 24.5,
            "timestamp": int(datetime.now().timestamp()) + 7200  # 2小时后
        }
        
        response = client.post("/api/v1/upload", json=payload)
        assert response.status_code == 422
    
    def test_get_package_history(self, client):
        """测试获取包裹历史记录"""
        # 先上传几条数据
        package_id = 1001
        for i in range(3):
            payload = {
                "package_id": package_id,
                "temperature": 20.0 + i,
                "timestamp": int(datetime.now().timestamp()) - i * 3600
            }
            client.post("/api/v1/upload", json=payload)
        
        # 查询历史记录
        response = client.get(f"/api/v1/packages/{package_id}/records")
        
        assert response.status_code == 200
        data = response.json()
        assert data["package_id"] == package_id
        assert data["total_records"] == 3
        assert len(data["records"]) == 3
    
    def test_get_package_history_with_pagination(self, client):
        """测试分页查询"""
        package_id = 1002
        
        # 上传5条数据
        for i in range(5):
            payload = {
                "package_id": package_id,
                "temperature": 20.0 + i,
                "timestamp": int(datetime.now().timestamp()) - i * 3600
            }
            client.post("/api/v1/upload", json=payload)
        
        # 查询前2条
        response = client.get(f"/api/v1/packages/{package_id}/records?limit=2&offset=0")
        data = response.json()
        assert len(data["records"]) == 2
        assert data["total_records"] == 5
        
        # 查询接下来的2条
        response = client.get(f"/api/v1/packages/{package_id}/records?limit=2&offset=2")
        data = response.json()
        assert len(data["records"]) == 2
    
    def test_get_latest_record(self, client):
        """测试获取最新记录"""
        package_id = 1003
        
        # 上传多条数据
        timestamps = []
        for i in range(3):
            ts = int(datetime.now().timestamp()) - i * 3600
            timestamps.append(ts)
            payload = {
                "package_id": package_id,
                "temperature": 20.0 + i,
                "timestamp": ts
            }
            client.post("/api/v1/upload", json=payload)
        
        # 获取最新记录
        response = client.get(f"/api/v1/packages/{package_id}/latest")
        
        assert response.status_code == 200
        data = response.json()
        assert data["package_id"] == package_id
        assert data["timestamp"] == max(timestamps)  # 应该是最新的时间戳
    
    def test_get_latest_record_not_found(self, client):
        """测试获取不存在的包裹记录"""
        response = client.get("/api/v1/packages/9999/latest")
        assert response.status_code == 404
