#!/usr/bin/env python3
"""
创建设备表的数据库迁移脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings
from loguru import logger


def create_device_table():
    """创建设备表"""
    try:
        # 创建数据库引擎
        engine = create_engine(settings.database_url)
        
        logger.info("开始创建设备表...")
        
        # 创建设备表
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '设备ID',
                    device_id VARCHAR(50) UNIQUE NOT NULL COMMENT '设备唯一标识（如：ESP32-001）',
                    device_name VARCHAR(100) NULL COMMENT '设备名称',
                    secret_key VARCHAR(64) NOT NULL COMMENT 'HMAC密钥（用于签名）',
                    is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否激活',
                    description TEXT NULL COMMENT '设备描述',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新时间',
                    last_seen TIMESTAMP NULL COMMENT '最后活跃时间',
                    INDEX idx_device_id (device_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ESP32 设备表';
            """))
            conn.commit()
        
        logger.success("设备表创建成功！")
        
    except Exception as e:
        logger.error(f"创建设备表失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("=== 设备表创建脚本 ===")
    
    try:
        create_device_table()
        logger.success("所有操作完成！")
        
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

