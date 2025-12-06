from fastapi import HTTPException, status


class PackageNotFoundException(HTTPException):
    """包裹未找到异常"""
    def __init__(self, package_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package with ID {package_id} not found"
        )


class DatabaseConnectionError(HTTPException):
    """数据库连接错误"""
    def __init__(self, detail: str = "Database connection failed"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class InvalidDataError(HTTPException):
    """无效数据错误"""
    def __init__(self, detail: str = "Invalid data provided"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
