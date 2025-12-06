from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # MySQL 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str = "rfid_system"
    
    # 应用配置
    APP_NAME: str = "RFID Cold Chain Monitor"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 温度阈值配置（可选）
    TEMP_HIGH_THRESHOLD: float = 30.0
    TEMP_LOW_THRESHOLD: float = -10.0
    
    @property
    def database_url(self) -> str:
        """构建数据库连接 URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
