#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有表结构
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import engine, Base
from app.models import PackageRecord  # 导入所有模型
from loguru import logger


def init_database():
    """初始化数据库"""
    try:
        logger.info("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        # 打印创建的表
        logger.info(f"📋 Created tables: {list(Base.metadata.tables.keys())}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
