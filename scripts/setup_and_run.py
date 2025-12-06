#!/usr/bin/env python3
"""
设置和运行脚本
"""

import sys
import os
import subprocess
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """检查依赖"""
    logger.info("检查依赖...")
    
    try:
        import fastapi
        import sqlalchemy
        import pymysql
        import jose
        import passlib
        logger.success("所有依赖已安装")
        return True
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.info("请运行: pip install -r requirements.txt")
        return False


def check_env_file():
    """检查环境配置文件"""
    logger.info("检查环境配置文件...")
    
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            logger.warning(".env 文件不存在，请复制 .env.example 并配置")
            logger.info(f"cp {env_example} {env_file}")
        else:
            logger.error("环境配置文件不存在")
        return False
    
    logger.success("环境配置文件存在")
    return True


def run_database_migration():
    """运行数据库迁移"""
    logger.info("运行数据库迁移...")
    
    try:
        # 运行用户表创建脚本
        script_path = project_root / "scripts" / "create_user_tables.py"
        subprocess.run([sys.executable, str(script_path)], check=True)
        logger.success("数据库迁移完成")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"数据库迁移失败: {e}")
        return False
    except Exception as e:
        logger.error(f"运行迁移脚本失败: {e}")
        return False


def start_server():
    """启动服务器"""
    logger.info("启动服务器...")
    
    try:
        # 使用uvicorn启动服务器
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        logger.info("服务器启动命令: " + " ".join(cmd))
        logger.info("服务器将在 http://localhost:8000 启动")
        logger.info("API文档: http://localhost:8000/api/v1/docs")
        logger.info("按 Ctrl+C 停止服务器")
        
        subprocess.run(cmd, cwd=project_root)
        
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"启动服务器失败: {e}")


def main():
    """主函数"""
    logger.info("=== RFID 包裹监控系统启动脚本 ===")
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查环境配置
    if not check_env_file():
        return
    
    # 运行数据库迁移
    if not run_database_migration():
        logger.warning("数据库迁移失败，但仍尝试启动服务器")
    
    # 启动服务器
    start_server()


if __name__ == "__main__":
    main()
