from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    健康检查接口
    
    检查应用和数据库连接状态
    """
    # 检查数据库连接
    try:
        # 使用text()包装SQL语句以适配SQLAlchemy 2.0
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        result.fetchone()  # 确保查询执行成功
        db_status = "connected"
    except Exception as e:
        print(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        database=db_status,
        app_name=settings.APP_NAME,
        version=settings.API_VERSION
    )
