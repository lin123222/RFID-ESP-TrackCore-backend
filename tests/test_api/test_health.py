"""
健康检查 API 测试
"""


class TestHealthAPI:
    """健康检查 API 测试类"""
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "app_name" in data
        assert "version" in data
        assert data["app_name"] == "RFID Cold Chain Monitor"
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
