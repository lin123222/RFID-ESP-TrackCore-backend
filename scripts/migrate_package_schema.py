#!/usr/bin/env python3
"""
数据库迁移脚本：更新包裹记录表结构
将单一温度字段扩展为最高温度、平均湿度、超阈值时间
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from app.core.database import engine, SessionLocal
from app.models.package import PackageRecord
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_column_exists(table_name: str, column_name: str) -> bool:
    """检查表中是否存在指定列"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_schema():
    """执行数据库架构迁移"""
    db = SessionLocal()
    
    try:
        logger.info("开始数据库迁移...")
        
        # 1. 检查是否需要迁移
        has_new_fields = check_column_exists('package_records', 'max_temperature')
        has_old_field = check_column_exists('package_records', 'temperature')
        
        if has_new_fields and not has_old_field:
            logger.info("数据库已经是最新版本，无需迁移")
            return
        elif has_new_fields and has_old_field:
            logger.info("检测到新字段已存在但旧字段未删除，继续删除旧字段...")
            # 跳转到删除旧字段的步骤
            logger.info("删除旧的temperature字段...")
            db.execute(text("""
                ALTER TABLE package_records 
                DROP COLUMN temperature
            """))
            db.commit()
            logger.info("旧字段删除完成！")
            return
        
        # 2. 创建备份表
        logger.info("创建备份表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS package_records_backup AS 
            SELECT * FROM package_records
        """))
        
        # 3. 添加新字段
        logger.info("添加新字段...")
        
        # 添加max_temperature字段
        db.execute(text("""
            ALTER TABLE package_records 
            ADD COLUMN max_temperature REAL
        """))
        
        # 添加avg_humidity字段
        db.execute(text("""
            ALTER TABLE package_records 
            ADD COLUMN avg_humidity REAL
        """))
        
        # 添加over_threshold_time字段
        db.execute(text("""
            ALTER TABLE package_records 
            ADD COLUMN over_threshold_time INTEGER
        """))
        
        # 4. 迁移现有数据
        logger.info("迁移现有数据...")
        db.execute(text("""
            UPDATE package_records 
            SET max_temperature = temperature,
                avg_humidity = 50.0,
                over_threshold_time = 0
            WHERE max_temperature IS NULL
        """))
        
        # 5. 设置字段为非空（MySQL支持ALTER COLUMN MODIFY）
        logger.info("设置字段为非空...")
        
        # MySQL语法：修改字段为非空
        db.execute(text("""
            ALTER TABLE package_records 
            MODIFY COLUMN max_temperature FLOAT NOT NULL
        """))
        
        db.execute(text("""
            ALTER TABLE package_records 
            MODIFY COLUMN avg_humidity FLOAT NOT NULL
        """))
        
        db.execute(text("""
            ALTER TABLE package_records 
            MODIFY COLUMN over_threshold_time INT NOT NULL
        """))
        
        # 6. 删除旧的temperature字段
        logger.info("删除旧的temperature字段...")
        db.execute(text("""
            ALTER TABLE package_records 
            DROP COLUMN temperature
        """))
        
        # 7. 提交更改
        db.commit()
        
        # 8. 验证迁移结果
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(max_temperature) as max_temp_count,
                COUNT(avg_humidity) as humidity_count,
                COUNT(over_threshold_time) as over_time_count
            FROM package_records
        """)).fetchone()
        
        logger.info(f"迁移完成！统计信息：")
        logger.info(f"  总记录数: {result.total_records}")
        logger.info(f"  最高温度记录数: {result.max_temp_count}")
        logger.info(f"  湿度记录数: {result.humidity_count}")
        logger.info(f"  超阈值时间记录数: {result.over_time_count}")
        
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """回滚迁移（从备份恢复）"""
    db = SessionLocal()
    
    try:
        logger.info("开始回滚迁移...")
        
        # 检查备份表是否存在
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if 'package_records_backup' not in tables:
            logger.error("备份表不存在，无法回滚")
            return
        
        # MySQL语法：删除当前表并从备份恢复
        db.execute(text("DROP TABLE IF EXISTS package_records"))
        db.execute(text("RENAME TABLE package_records_backup TO package_records"))
        
        db.commit()
        logger.info("回滚完成")
        
    except Exception as e:
        logger.error(f"回滚失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        migrate_schema()
