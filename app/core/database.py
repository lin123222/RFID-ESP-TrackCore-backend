from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 连接池预检查
    pool_recycle=3600,   # 连接回收时间（秒）
    echo=settings.DEBUG  # 是否打印 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖注入函数
    用于 FastAPI 的 Depends
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库
    创建所有表
    """
    Base.metadata.create_all(bind=engine)
