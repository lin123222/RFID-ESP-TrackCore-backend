#!/usr/bin/env python3
"""
测试数据填充脚本
用于开发和测试
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.package import PackageRecord
from loguru import logger


def generate_test_data(num_packages: int = 3, records_per_package: int = 10):
    """
    生成测试数据
    
    Args:
        num_packages: 包裹数量
        records_per_package: 每个包裹的记录数
    """
    db = SessionLocal()
    
    try:
        logger.info(f"🌱 Generating test data...")
        logger.info(f"   Packages: {num_packages}")
        logger.info(f"   Records per package: {records_per_package}")
        
        base_time = datetime.now()
        
        for package_id in range(1001, 1001 + num_packages):
            for i in range(records_per_package):
                # 生成随机温度（20-30°C，偶尔有异常值）
                if random.random() < 0.1:  # 10% 概率异常
                    temperature = random.choice([
                        random.uniform(-15, -5),  # 低温异常
                        random.uniform(35, 45)    # 高温异常
                    ])
                else:
                    temperature = random.uniform(20, 30)
                
                # 生成时间戳（从现在往前推）
                time_offset = timedelta(hours=i)
                record_time = base_time - time_offset
                timestamp = int(record_time.timestamp())
                
                record = PackageRecord(
                    package_id=package_id,
                    temperature=round(temperature, 2),
                    timestamp=timestamp
                )
                db.add(record)
        
        db.commit()
        logger.info(f"✅ Successfully created {num_packages * records_per_package} test records")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to generate test data: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    generate_test_data(num_packages=3, records_per_package=20)
