#!/usr/bin/env python3
"""
创建用户相关表的数据库迁移脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.user import User, UserPackage
from loguru import logger


def create_user_tables():
    """创建用户相关表"""
    try:
        # 创建数据库引擎
        engine = create_engine(settings.database_url)
        
        logger.info("开始创建用户相关表...")
        
        # 创建用户表
        logger.info("创建 users 表...")
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
                    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
                    email VARCHAR(100) NULL COMMENT '邮箱',
                    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
                    nickname VARCHAR(100) NULL COMMENT '昵称',
                    status INT DEFAULT 1 NOT NULL COMMENT '状态: 1正常 0禁用',
                    is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否激活',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新时间',
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
            """))
            conn.commit()
        
        # 创建用户包裹关联表
        logger.info("创建 user_packages 表...")
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_packages (
                    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '关联ID',
                    user_id INT NOT NULL COMMENT '用户ID',
                    package_id INT NOT NULL COMMENT '包裹ID',
                    package_name VARCHAR(100) NULL COMMENT '包裹名称',
                    description VARCHAR(500) NULL COMMENT '包裹描述',
                    is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否激活',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新时间',
                    INDEX idx_user_id (user_id),
                    INDEX idx_package_id (package_id),
                    UNIQUE KEY uk_user_package (user_id, package_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户包裹关联表';
            """))
            conn.commit()
        
        logger.success("用户相关表创建成功！")
        
        # 创建测试用户
        create_test_user(engine)
        
    except Exception as e:
        logger.error(f"创建用户表失败: {e}")
        raise


def create_test_user(engine):
    """创建测试用户"""
    try:
        # 直接使用bcrypt生成密码哈希，避免导入问题
        import bcrypt
        
        logger.info("创建测试用户...")
        
        # 生成密码哈希
        password = "123456"
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        with engine.connect() as conn:
            # 检查是否已存在测试用户
            result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
            if result.fetchone():
                logger.info("测试用户已存在，跳过创建")
                return
            
            # 创建测试用户
            conn.execute(text("""
                INSERT INTO users (username, email, password_hash, nickname, status, is_active)
                VALUES ('admin', 'admin@example.com', :password_hash, '管理员', 1, 1)
            """), {"password_hash": password_hash})
            conn.commit()
        
        logger.success("测试用户创建成功！")
        logger.info("测试用户信息:")
        logger.info("  用户名: admin")
        logger.info("  密码: 123456")
        logger.info("  邮箱: admin@example.com")
        
    except Exception as e:
        logger.error(f"创建测试用户失败: {e}")


def main():
    """主函数"""
    logger.info("=== 用户表创建脚本 ===")
    
    try:
        create_user_tables()
        logger.success("所有操作完成！")
        
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
