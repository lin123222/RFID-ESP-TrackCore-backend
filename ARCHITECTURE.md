# 后端架构与业务逻辑文档

## 📋 文档概述

本文档详细说明后端系统的架构设计、业务逻辑、代码组织和维护指南，方便开发人员理解、修改和扩展系统功能。

---

## 🏗️ 系统架构

### 架构模式

本项目采用**分层架构（Layered Architecture）**，将系统划分为以下几层：

```
┌─────────────────────────────────────────┐
│         API 路由层 (API Layer)          │  ← HTTP 请求入口
├─────────────────────────────────────────┤
│      业务逻辑层 (Service Layer)         │  ← 核心业务处理
├─────────────────────────────────────────┤
│     数据访问层 (Repository Layer)       │  ← 数据库操作
├─────────────────────────────────────────┤
│       数据模型层 (Model Layer)          │  ← ORM 模型定义
├─────────────────────────────────────────┤
│         数据库 (MySQL Database)         │  ← 数据持久化
└─────────────────────────────────────────┘

辅助层：
├── 数据验证层 (Schema Layer)    - Pydantic 模型
├── 核心配置层 (Core Layer)       - 配置和数据库连接
└── 工具层 (Utils Layer)          - 日志、异常等
```

### 架构优势

1. **高内聚低耦合**：每层职责单一，互不干扰
2. **易于测试**：可以独立测试每一层
3. **便于扩展**：新增功能只需在对应层添加代码
4. **代码复用**：业务逻辑可在多个接口中复用
5. **团队协作**：不同开发者可并行开发不同层

---

## 📁 目录结构详解

```
network_backend/
├── app/                           # 应用主目录
│   ├── api/                       # API 路由层
│   │   ├── deps.py               # 依赖注入函数
│   │   └── v1/                   # API v1 版本
│   │       ├── endpoints/        # 具体的路由端点
│   │       │   ├── health.py    # 健康检查接口
│   │       │   └── package.py   # 包裹相关接口
│   │       └── router.py         # 路由聚合器
│   │
│   ├── core/                      # 核心配置层
│   │   ├── config.py             # 配置管理（环境变量）
│   │   └── database.py           # 数据库连接和会话管理
│   │
│   ├── models/                    # 数据模型层（ORM）
│   │   └── package.py            # PackageRecord 模型
│   │
│   ├── schemas/                   # 数据验证层（Pydantic）
│   │   ├── common.py             # 通用响应模型
│   │   └── package.py            # 包裹数据模型
│   │
│   ├── services/                  # 业务逻辑层
│   │   └── package_service.py    # 包裹业务逻辑
│   │
│   ├── repositories/              # 数据访问层
│   │   └── package_repository.py # 包裹数据库操作
│   │
│   ├── utils/                     # 工具层
│   │   ├── logger.py             # 日志配置
│   │   └── exceptions.py         # 自定义异常
│   │
│   └── main.py                    # 应用入口（FastAPI 实例）
│
├── scripts/                       # 工具脚本
│   ├── init_db.py                # 数据库初始化
│   └── seed_data.py              # 测试数据填充
│
├── tests/                         # 测试目录
│   ├── test_api/                 # API 测试
│   └── test_services/            # 服务层测试
│
├── alembic/                       # 数据库迁移
│   ├── versions/                 # 迁移脚本
│   └── env.py                    # Alembic 配置
│
├── logs/                          # 日志文件（运行时生成）
├── requirements.txt               # Python 依赖
├── .env                          # 环境变量（不提交到 Git）
├── .env.example                  # 环境变量模板
└── run.py                        # 启动脚本
```

---

## 🔄 数据流转详解

### 请求处理流程

```
1. ESP32 发送 HTTP POST 请求
   ↓
2. FastAPI 路由层接收请求 (package.py)
   ↓
3. Pydantic 自动验证请求数据 (schemas/package.py)
   ↓
4. 路由层调用业务逻辑层 (package_service.py)
   ↓
5. 业务层执行业务逻辑（温度检查、日志记录等）
   ↓
6. 业务层调用数据访问层 (package_repository.py)
   ↓
7. 数据访问层执行 SQL 操作（通过 SQLAlchemy ORM）
   ↓
8. 数据保存到 MySQL 数据库
   ↓
9. 逐层返回结果
   ↓
10. 路由层返回 JSON 响应给 ESP32
```

### 示例：上传数据的完整流程

```python
# 1. 路由层 (app/api/v1/endpoints/package.py)
@router.post("/upload")
async def upload_package_data(
    payload: PackageUploadRequest,  # 2. Pydantic 自动验证
    service: PackageService = Depends(get_package_service)  # 3. 依赖注入
):
    result = service.save_package_data(payload)  # 4. 调用业务层
    return result

# 5. 业务逻辑层 (app/services/package_service.py)
class PackageService:
    def save_package_data(self, data: PackageUploadRequest):
        # 6. 业务逻辑：温度检查
        self._check_temperature_alert(data.package_id, data.temperature)
        
        # 7. 调用数据访问层
        record = self.repository.create(data)
        
        # 8. 返回结果
        return {"status": "success", "record_id": record.id}

# 9. 数据访问层 (app/repositories/package_repository.py)
class PackageRepository:
    def create(self, data: PackageUploadRequest):
        # 10. 创建 ORM 对象
        db_record = PackageRecord(**data.dict())
        
        # 11. 保存到数据库
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        
        return db_record
```

---

## 📊 核心业务逻辑详解

### 1. 数据上传业务逻辑

**位置**: `app/services/package_service.py` → `save_package_data()`

**功能**：接收并保存包裹温度数据

**业务规则**：

```python
def save_package_data(self, data: PackageUploadRequest) -> Dict[str, Any]:
    """
    保存包裹数据的业务逻辑
    
    业务流程：
    1. 温度异常检测（高温/低温告警）
    2. 数据持久化到数据库
    3. 记录操作日志
    4. 返回操作结果
    
    Args:
        data: 包裹上传数据（已通过 Pydantic 验证）
        
    Returns:
        包含状态、消息和记录ID的字典
        
    Raises:
        Exception: 数据库操作失败时抛出
    """
    
    # 步骤1：温度异常检测
    self._check_temperature_alert(data.package_id, data.temperature)
    
    # 步骤2：保存数据
    try:
        record = self.repository.create(data)
        
        # 步骤3：记录日志
        logger.info(
            f"Package data saved - ID: {data.package_id}, "
            f"Temp: {data.temperature}°C, Timestamp: {data.timestamp}"
        )
        
        # 步骤4：返回结果
        return {
            "status": "success",
            "message": f"Data for package {data.package_id} received",
            "record_id": record.id
        }
    except Exception as e:
        logger.error(f"Failed to save package data: {str(e)}")
        raise
```

**温度告警逻辑**：

```python
def _check_temperature_alert(self, package_id: int, temperature: float) -> None:
    """
    检查温度是否异常并记录告警
    
    告警规则：
    - 高温告警：temperature > TEMP_HIGH_THRESHOLD (默认 30°C)
    - 低温告警：temperature < TEMP_LOW_THRESHOLD (默认 -10°C)
    
    Args:
        package_id: 包裹ID
        temperature: 温度值
    """
    if temperature > settings.TEMP_HIGH_THRESHOLD:
        logger.warning(
            f"⚠️ HIGH TEMPERATURE ALERT - Package {package_id}: "
            f"{temperature}°C (Threshold: {settings.TEMP_HIGH_THRESHOLD}°C)"
        )
        # TODO: 可以在这里添加告警通知逻辑（邮件、短信等）
    
    elif temperature < settings.TEMP_LOW_THRESHOLD:
        logger.warning(
            f"⚠️ LOW TEMPERATURE ALERT - Package {package_id}: "
            f"{temperature}°C (Threshold: {settings.TEMP_LOW_THRESHOLD}°C)"
        )
        # TODO: 可以在这里添加告警通知逻辑
```

---

### 2. 历史查询业务逻辑

**位置**: `app/services/package_service.py` → `get_package_history()`

**功能**：查询指定包裹的历史温度记录

**业务规则**：

```python
def get_package_history(
    self, 
    package_id: int, 
    limit: int = 100,
    offset: int = 0
) -> PackageHistoryResponse:
    """
    获取包裹历史记录
    
    业务流程：
    1. 查询数据库获取记录列表（按时间倒序）
    2. 统计总记录数
    3. 转换为响应模型
    
    Args:
        package_id: 包裹ID
        limit: 返回记录数量限制（1-1000）
        offset: 偏移量（用于分页）
        
    Returns:
        包含包裹ID、总记录数和记录列表的响应对象
    """
    # 步骤1：查询记录（按时间戳倒序）
    records = self.repository.get_by_package_id(package_id, limit, offset)
    
    # 步骤2：统计总数
    total = self.repository.count_by_package_id(package_id)
    
    # 步骤3：转换为响应模型
    return PackageHistoryResponse(
        package_id=package_id,
        total_records=total,
        records=[PackageRecordResponse.model_validate(r) for r in records]
    )
```

---

### 3. 最新记录查询逻辑

**位置**: `app/services/package_service.py` → `get_latest_record()`

**功能**：获取指定包裹的最新温度记录

**业务规则**：

```python
def get_latest_record(self, package_id: int) -> PackageRecordResponse | None:
    """
    获取包裹最新记录
    
    业务流程：
    1. 查询数据库获取最新记录（按时间戳倒序取第一条）
    2. 转换为响应模型
    
    Args:
        package_id: 包裹ID
        
    Returns:
        最新记录对象，如果不存在则返回 None
    """
    record = self.repository.get_latest_by_package_id(package_id)
    
    if record:
        return PackageRecordResponse.model_validate(record)
    return None
```

---

## 🗄️ 数据库操作详解

### 数据访问层职责

**位置**: `app/repositories/package_repository.py`

数据访问层封装了所有数据库操作，提供统一的接口给业务层调用。

### 核心方法说明

#### 1. 创建记录

```python
def create(self, data: PackageUploadRequest) -> PackageRecord:
    """
    创建新的包裹记录
    
    SQL 操作：
    INSERT INTO package_records (package_id, temperature, timestamp)
    VALUES (?, ?, ?)
    
    Args:
        data: 包裹上传数据
        
    Returns:
        创建的记录对象（包含自增的 ID）
    """
    db_record = PackageRecord(
        package_id=data.package_id,
        temperature=data.temperature,
        timestamp=data.timestamp
    )
    self.db.add(db_record)
    self.db.commit()
    self.db.refresh(db_record)  # 刷新以获取自增ID
    return db_record
```

#### 2. 按包裹ID查询

```python
def get_by_package_id(
    self, 
    package_id: int, 
    limit: int = 100,
    offset: int = 0
) -> List[PackageRecord]:
    """
    根据包裹ID获取历史记录
    
    SQL 操作：
    SELECT * FROM package_records
    WHERE package_id = ?
    ORDER BY timestamp DESC
    LIMIT ? OFFSET ?
    
    Args:
        package_id: 包裹ID
        limit: 返回记录数量限制
        offset: 偏移量（用于分页）
        
    Returns:
        记录列表（按时间戳倒序）
    """
    return self.db.query(PackageRecord).filter(
        PackageRecord.package_id == package_id
    ).order_by(
        desc(PackageRecord.timestamp)
    ).limit(limit).offset(offset).all()
```

#### 3. 统计记录数

```python
def count_by_package_id(self, package_id: int) -> int:
    """
    统计指定包裹的记录数量
    
    SQL 操作：
    SELECT COUNT(*) FROM package_records
    WHERE package_id = ?
    
    Args:
        package_id: 包裹ID
        
    Returns:
        记录数量
    """
    return self.db.query(PackageRecord).filter(
        PackageRecord.package_id == package_id
    ).count()
```

#### 4. 获取最新记录

```python
def get_latest_by_package_id(self, package_id: int) -> Optional[PackageRecord]:
    """
    获取指定包裹的最新记录
    
    SQL 操作：
    SELECT * FROM package_records
    WHERE package_id = ?
    ORDER BY timestamp DESC
    LIMIT 1
    
    Args:
        package_id: 包裹ID
        
    Returns:
        最新记录或 None
    """
    return self.db.query(PackageRecord).filter(
        PackageRecord.package_id == package_id
    ).order_by(
        desc(PackageRecord.timestamp)
    ).first()
```

---

## 🔐 数据验证规则

### Pydantic Schema 验证

**位置**: `app/schemas/package.py`

所有进入系统的数据都会经过 Pydantic 验证，确保数据类型和格式正确。

### 上传请求验证

```python
class PackageUploadRequest(BaseModel):
    """包裹数据上传请求模型"""
    
    # 包裹ID验证
    package_id: int = Field(
        ...,                    # 必填
        gt=0,                   # 必须大于0
        description="包裹ID，必须为正整数",
        example=1001
    )
    
    # 温度验证
    temperature: float = Field(
        ...,                    # 必填
        ge=-50.0,              # 大于等于 -50
        le=100.0,              # 小于等于 100
        description="温度值(°C)，范围: -50 ~ 100",
        example=24.5
    )
    
    # 时间戳验证
    timestamp: int = Field(
        ...,                    # 必填
        gt=0,                   # 必须大于0
        description="Unix时间戳（秒）",
        example=1700000000
    )
    
    # 自定义验证器：检查时间戳是否合理
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """验证时间戳不能是未来时间"""
        current_timestamp = int(datetime.now().timestamp())
        if v > current_timestamp + 3600:  # 允许1小时误差
            raise ValueError("时间戳不能是未来时间")
        return v
```

### 验证失败示例

```python
# 示例1：package_id 为负数
{
  "package_id": -1,        # ❌ 验证失败
  "temperature": 24.5,
  "timestamp": 1700000000
}
# 错误：Input should be greater than 0

# 示例2：温度超出范围
{
  "package_id": 1001,
  "temperature": 150.0,    # ❌ 验证失败
  "timestamp": 1700000000
}
# 错误：Input should be less than or equal to 100

# 示例3：未来时间戳
{
  "package_id": 1001,
  "temperature": 24.5,
  "timestamp": 9999999999  # ❌ 验证失败
}
# 错误：时间戳不能是未来时间
```

---

## ⚙️ 配置管理

### 环境变量配置

**位置**: `app/core/config.py`

所有配置通过环境变量管理，支持不同环境（开发、测试、生产）的配置切换。

```python
class Settings(BaseSettings):
    """应用配置类"""
    
    # MySQL 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str              # 必填，从 .env 读取
    MYSQL_DATABASE: str = "rfid_system"
    
    # 应用配置
    APP_NAME: str = "RFID Cold Chain Monitor"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 温度阈值配置
    TEMP_HIGH_THRESHOLD: float = 30.0   # 高温阈值
    TEMP_LOW_THRESHOLD: float = -10.0   # 低温阈值
    
    @property
    def database_url(self) -> str:
        """构建数据库连接 URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

### 配置使用示例

```python
from app.core.config import settings

# 获取配置
db_url = settings.database_url
high_temp = settings.TEMP_HIGH_THRESHOLD

# 在业务逻辑中使用
if temperature > settings.TEMP_HIGH_THRESHOLD:
    logger.warning("High temperature alert!")
```

---

## 🔧 如何修改和扩展

### 场景1：添加新的数据字段

**需求**：在包裹记录中添加"湿度"字段

**步骤**：

1. **修改数据模型** (`app/models/package.py`)

```python
class PackageRecord(Base):
    __tablename__ = "package_records"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=True)  # ← 新增字段
    timestamp = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

2. **修改数据验证模型** (`app/schemas/package.py`)

```python
class PackageUploadRequest(BaseModel):
    package_id: int = Field(..., gt=0)
    temperature: float = Field(..., ge=-50.0, le=100.0)
    humidity: float = Field(..., ge=0.0, le=100.0)  # ← 新增字段
    timestamp: int = Field(..., gt=0)
```

3. **创建数据库迁移**

```bash
alembic revision --autogenerate -m "Add humidity field"
alembic upgrade head
```

4. **修改业务逻辑**（如需要）

```python
def save_package_data(self, data: PackageUploadRequest):
    # 可以添加湿度检查逻辑
    if data.humidity > 80:
        logger.warning(f"High humidity alert: {data.humidity}%")
    
    record = self.repository.create(data)
    return {"status": "success", "record_id": record.id}
```

---

### 场景2：添加新的业务接口

**需求**：添加"删除记录"接口

**步骤**：

1. **在数据访问层添加方法** (`app/repositories/package_repository.py`)

```python
def delete_by_id(self, record_id: int) -> bool:
    """删除指定记录"""
    record = self.get_by_id(record_id)
    if record:
        self.db.delete(record)
        self.db.commit()
        return True
    return False
```

2. **在业务逻辑层添加方法** (`app/services/package_service.py`)

```python
def delete_record(self, record_id: int) -> Dict[str, Any]:
    """删除记录的业务逻辑"""
    if self.repository.delete_by_id(record_id):
        logger.info(f"Record {record_id} deleted")
        return {"status": "success", "message": "Record deleted"}
    else:
        raise HTTPException(status_code=404, detail="Record not found")
```

3. **在路由层添加接口** (`app/api/v1/endpoints/package.py`)

```python
@router.delete("/records/{record_id}", tags=["Package"])
async def delete_record(
    record_id: int,
    service: PackageService = Depends(get_package_service)
):
    """删除指定记录"""
    return service.delete_record(record_id)
```

---

### 场景3：修改温度阈值

**方法1：修改环境变量** (推荐)

编辑 `.env` 文件：

```env
TEMP_HIGH_THRESHOLD=35.0
TEMP_LOW_THRESHOLD=-15.0
```

**方法2：修改配置类**

编辑 `app/core/config.py`：

```python
class Settings(BaseSettings):
    TEMP_HIGH_THRESHOLD: float = 35.0  # 修改默认值
    TEMP_LOW_THRESHOLD: float = -15.0
```

---

### 场景4：添加告警通知

**需求**：温度异常时发送邮件通知

**步骤**：

1. **安装邮件库**

```bash
pip install aiosmtplib
```

2. **创建邮件工具** (`app/utils/email.py`)

```python
import aiosmtplib
from email.message import EmailMessage

async def send_alert_email(package_id: int, temperature: float):
    """发送告警邮件"""
    message = EmailMessage()
    message["From"] = "alert@example.com"
    message["To"] = "admin@example.com"
    message["Subject"] = f"Temperature Alert - Package {package_id}"
    message.set_content(
        f"Package {package_id} temperature: {temperature}°C"
    )
    
    await aiosmtplib.send(
        message,
        hostname="smtp.example.com",
        port=587,
        username="alert@example.com",
        password="password"
    )
```

3. **在业务逻辑中调用**

```python
async def _check_temperature_alert(self, package_id: int, temperature: float):
    if temperature > settings.TEMP_HIGH_THRESHOLD:
        logger.warning(f"High temperature alert: {temperature}°C")
        # 发送邮件
        await send_alert_email(package_id, temperature)
```

---

## 📊 数据库表结构

### package_records 表

```sql
CREATE TABLE `package_records` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
  `package_id` INT NOT NULL COMMENT '包裹ID',
  `temperature` FLOAT NOT NULL COMMENT '温度值(°C)',
  `timestamp` BIGINT NOT NULL COMMENT 'Unix时间戳',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  
  INDEX `idx_package_id` (`package_id`),
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_package_timestamp` (`package_id`, `timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='包裹温度记录表';
```

### 索引说明

- **idx_package_id**: 用于快速查询指定包裹的所有记录
- **idx_timestamp**: 用于按时间范围查询
- **idx_package_timestamp**: 复合索引，优化同时按包裹和时间查询的性能

---

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api/test_package.py

# 查看测试覆盖率
pytest --cov=app tests/
```

### 测试结构

```
tests/
├── test_api/              # API 集成测试
│   ├── test_health.py    # 健康检查测试
│   └── test_package.py   # 包裹接口测试
└── test_services/         # 服务层单元测试
    └── test_package_service.py
```

### 编写新测试

```python
# tests/test_api/test_new_feature.py
def test_new_feature(client):
    """测试新功能"""
    response = client.post("/api/v1/new-endpoint", json={...})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

---

## 📝 日志系统

### 日志配置

**位置**: `app/utils/logger.py`

日志同时输出到控制台和文件：

- **控制台**: 彩色输出，便于开发调试
- **文件**: 每天自动轮转，保留30天

### 日志级别

```python
logger.debug("调试信息")      # DEBUG
logger.info("普通信息")       # INFO
logger.warning("警告信息")    # WARNING
logger.error("错误信息")      # ERROR
logger.critical("严重错误")   # CRITICAL
```

### 日志使用示例

```python
from loguru import logger

# 记录操作
logger.info(f"Package {package_id} data saved")

# 记录告警
logger.warning(f"High temperature: {temperature}°C")

# 记录错误
logger.error(f"Database error: {str(e)}")
```

### 日志文件位置

```
logs/
├── app_2024-11-26.log
├── app_2024-11-27.log
└── ...
```

---

## 🔒 安全建议

### 1. 环境变量管理

- ❌ **不要**将 `.env` 文件提交到 Git
- ✅ **使用** `.env.example` 作为模板
- ✅ **生产环境**使用强密码

### 2. 数据库安全

- ✅ 使用参数化查询（SQLAlchemy 自动处理）
- ✅ 限制数据库用户权限
- ✅ 定期备份数据

### 3. API 安全

- ✅ 使用 HTTPS（生产环境）
- ✅ 限制 CORS 允许的域名
- ✅ 添加请求频率限制（可选）

---

## 🐛 常见问题排查

### 问题1：数据库连接失败

**检查**：
1. MySQL 服务是否启动
2. `.env` 中的数据库配置是否正确
3. 数据库是否已创建

**解决**：
```bash
# 检查 MySQL 状态
systemctl status mysql

# 测试连接
mysql -h localhost -u root -p
```

### 问题2：导入错误

**原因**：模块导入路径错误

**解决**：确保使用绝对导入
```python
# ✅ 正确
from app.models.package import PackageRecord

# ❌ 错误
from models.package import PackageRecord
```

### 问题3：Alembic 迁移失败

**解决**：
```bash
# 查看当前版本
alembic current

# 重置迁移
alembic downgrade base
alembic upgrade head
```

---

## 📚 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)

---

## 📞 维护联系

如有问题或建议，请联系开发团队。

**文档版本**: 1.0.0  
**最后更新**: 2024-11-26  
**维护人员**: 后端开发团队
