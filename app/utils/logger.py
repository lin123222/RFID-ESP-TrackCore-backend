import sys
from loguru import logger
from app.core.config import settings


def setup_logger():
    """配置日志系统"""
    
    # 移除默认的 logger
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留30天
        compression="zip"  # 压缩旧日志
    )
    
    return logger
