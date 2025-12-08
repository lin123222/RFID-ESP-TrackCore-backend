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
│   │   ├── deps.py               # 依赖注入函数（用户认证、设备认证）
│   │   └── v1/                   # API v1 版本
│   │       ├── endpoints/        # 具体的路由端点
│   │       │   ├── health.py    # 健康检查接口
│   │       │   ├── package.py   # 包裹数据上传和查询接口
│   │       │   ├── auth.py      # 用户认证接口（注册、登录）
│   │       │   ├── user_packages.py  # 用户包裹管理接口
│   │       │   └── device.py   # 设备管理接口
│   │       └── router.py         # 路由聚合器
│   │
│   ├── core/                      # 核心配置层
│   │   ├── config.py             # 配置管理（环境变量）
│   │   └── database.py           # 数据库连接和会话管理
│   │
│   ├── models/                    # 数据模型层（ORM）
│   │   ├── package.py            # PackageRecord 模型
│   │   ├── user.py               # User、UserPackage 模型
│   │   └── device.py             # Device 模型
│   │
│   ├── schemas/                   # 数据验证层（Pydantic）
│   │   ├── common.py             # 通用响应模型
│   │   ├── package.py            # 包裹数据模型
│   │   ├── user.py               # 用户数据模型
│   │   └── device.py             # 设备数据模型
│   │
│   ├── services/                  # 业务逻辑层
│   │   ├── package_service.py    # 包裹业务逻辑
│   │   └── user.py               # 用户和包裹绑定业务逻辑
│   │
│   ├── repositories/              # 数据访问层
│   │   ├── package_repository.py # 包裹数据库操作
│   │   ├── user.py               # 用户和包裹绑定数据库操作
│   │   └── device_repository.py  # 设备数据库操作
│   │
│   ├── utils/                     # 工具层
│   │   ├── logger.py             # 日志配置
│   │   ├── auth.py               # JWT 认证工具
│   │   ├── security.py           # HMAC-SHA256 签名工具
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
1. ESP32 发送 HTTP POST 请求（带设备认证头）
   ↓
2. FastAPI 路由层接收请求 (package.py)
   ↓
3. 设备认证中间件验证 (deps.py → verify_device_authentication)
   - 验证 X-Device-ID、X-Signature、X-Timestamp
   - 检查设备是否存在且激活
   - 验证 HMAC-SHA256 签名
   ↓
4. Pydantic 自动验证请求数据 (schemas/package.py)
   ↓
5. 路由层调用业务逻辑层 (package_service.py)
   ↓
6. 业务层执行业务逻辑（温度检查、日志记录等）
   ↓
7. 业务层调用数据访问层 (package_repository.py)
   ↓
8. 数据访问层执行 SQL 操作（通过 SQLAlchemy ORM）
   ↓
9. 数据保存到 MySQL 数据库
   ↓
10. 逐层返回结果
   ↓
11. 路由层返回 JSON 响应给 ESP32

用户查询流程：
1. 用户发送 HTTP GET 请求（带 JWT Token）
   ↓
2. FastAPI 路由层接收请求 (package.py)
   ↓
3. JWT 认证中间件验证 (deps.py → get_current_user)
   - 验证 Token 有效性
   - 提取用户信息
   ↓
4. 权限检查（检查包裹所有权）
   - 查询 user_packages 表
   - 验证用户是否绑定该包裹
   ↓
5. 查询包裹记录
   ↓
6. 返回结果给用户
```

### 示例：上传数据的完整流程

```python
# 1. 路由层 (app/api/v1/endpoints/package.py)
@router.post("/upload")
async def upload_package_data(
    payload: PackageUploadRequest,  # 2. Pydantic 自动验证
    device: Device = Depends(verify_device_authentication),  # 设备认证
    service: PackageService = Depends(get_package_service)  # 3. 依赖注入
):
    result = service.save_package_data(payload)  # 4. 调用业务层
    return result

# 设备认证 (app/api/deps.py)
async def verify_device_authentication(
    x_device_id: str = Header(...),
    x_signature: str = Header(...),
    x_timestamp: int = Header(...),
    payload: PackageUploadRequest,
    device_repo: DeviceRepository = Depends(get_device_repository)
) -> Device:
    # 验证设备ID、签名、时间戳
    device = device_repo.get_by_device_id(x_device_id)
    # 验证 HMAC-SHA256 签名
    verify_hmac_signature(sign_data, x_signature, device.secret_key)
    return device

# 5. 业务逻辑层 (app/services/package_service.py)
class PackageService:
    def save_package_data(self, data: PackageUploadRequest):
        # 6. 业务逻辑：温度检查
        self._check_temperature_alert(data.package_id, data.max_temperature)
        
        # 7. 调用数据访问层
        record = self.repository.create(data)
        
        # 8. 返回结果
        return {"status": "success", "record_id": record.id}

# 9. 数据访问层 (app/repositories/package_repository.py)
class PackageRepository:
    def create(self, data: PackageUploadRequest):
        # 10. 创建 ORM 对象
        db_record = PackageRecord(
            package_id=data.package_id,
            max_temperature=data.max_temperature,
            avg_humidity=data.avg_humidity,
            over_threshold_time=data.over_threshold_time,
            timestamp=data.timestamp
        )
        
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
    保存包裹站点数据的业务逻辑
    
    业务流程：
    1. 温度异常检测（高温/低温告警）
    2. 数据持久化到数据库
    3. 记录操作日志
    4. 返回操作结果
    
    Args:
        data: 包裹上传数据（已通过 Pydantic 验证）
            - package_id: 包裹ID
            - max_temperature: 最高温度
            - avg_humidity: 平均湿度
            - over_threshold_time: 超阈值时间
            - timestamp: Unix时间戳
        
    Returns:
        包含状态、消息和记录ID的字典
        
    Raises:
        Exception: 数据库操作失败时抛出
    """
    
    # 步骤1：温度异常检测
    self._check_temperature_alert(data.package_id, data.max_temperature)
    
    # 步骤2：保存数据
    try:
        record = self.repository.create(data)
        
        # 步骤3：记录日志
        logger.info(
            f"Package data saved - ID: {data.package_id}, "
            f"MaxTemp: {data.max_temperature}°C, AvgHumidity: {data.avg_humidity}%, "
            f"OverTime: {data.over_threshold_time}s, Timestamp: {data.timestamp}"
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
        temperature: 最高温度值
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

### 2. 历史查询业务逻辑（带权限控制）

**位置**: `app/api/v1/endpoints/package.py` → `get_package_history()`

**功能**：查询指定包裹的所有站点记录（需要用户认证和权限检查）

**业务规则**：

```python
@router.get("/packages/{package_id}/records")
async def get_package_history(
    package_id: int,
    current_user: TokenData = Depends(get_current_user),  # 用户认证
    service: PackageService = Depends(get_package_service),
    user_package_repo: UserPackageRepository = Depends(get_user_package_repository)
):
    """
    获取包裹的所有站点记录（需要登录，只能查看自己的包裹）
    
    业务流程：
    1. 用户认证（JWT Token验证）
    2. 权限检查（检查包裹所有权）
    3. 查询数据库获取记录列表（按时间倒序）
    4. 统计总记录数
    5. 转换为响应模型
    
    Args:
        package_id: 包裹ID
        current_user: 当前登录用户（从JWT Token提取）
        service: 包裹业务服务
        user_package_repo: 用户包裹关联仓库
        
    Returns:
        包含包裹ID、总记录数和记录列表的响应对象
        
    Raises:
        HTTPException 403: 用户未绑定该包裹
    """
    # 步骤1：检查包裹所有权
    if not user_package_repo.check_package_ownership(current_user.user_id, package_id):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: You don't have permission to view package {package_id}"
        )
    
    # 步骤2：查询记录
    history = service.get_package_history(package_id, limit, offset)
    return history
```

**权限检查逻辑**：

```python
# app/repositories/user.py
def check_package_ownership(self, user_id: int, package_id: int) -> bool:
    """
    检查用户是否拥有指定包裹的访问权限
    
    SQL 操作：
    SELECT * FROM user_packages
    WHERE user_id = ? AND package_id = ? AND is_active = TRUE
    
    Args:
        user_id: 用户ID
        package_id: 包裹ID
        
    Returns:
        True 如果用户已绑定该包裹，否则 False
    """
    return self.db.query(UserPackage).filter(
        and_(
            UserPackage.user_id == user_id,
            UserPackage.package_id == package_id,
            UserPackage.is_active == True
        )
    ).first() is not None
```

---

### 3. 设备认证逻辑

**位置**: `app/api/deps.py` → `verify_device_authentication()`

**功能**：验证ESP32设备的身份和签名

**业务规则**：

```python
async def verify_device_authentication(
    request: Request,
    payload: PackageUploadRequest,
    x_device_id: Optional[str] = Header(None, alias="X-Device-ID"),
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    x_timestamp: Optional[int] = Header(None, alias="X-Timestamp"),
    device_repo: DeviceRepository = Depends(get_device_repository)
) -> Device:
    """
    验证设备身份和签名
    
    验证流程：
    1. 检查请求头是否包含必要字段
    2. 通过 device_id 查找设备
    3. 检查设备是否激活
    4. 构建签名字符串
    5. 验证 HMAC-SHA256 签名
    6. 验证时间戳（防重放攻击，允许±5分钟误差）
    7. 更新设备最后活跃时间
    
    Args:
        x_device_id: 设备ID（请求头）
        x_signature: HMAC签名（请求头）
        x_timestamp: 时间戳（请求头）
        payload: 请求体数据
        device_repo: 设备仓库
        
    Returns:
        验证通过的设备对象
        
    Raises:
        HTTPException 401: 设备ID无效、签名错误或时间戳超出范围
        HTTPException 403: 设备未激活
    """
    # 1. 检查请求头
    if not x_device_id or not x_signature or not x_timestamp:
        raise HTTPException(401, detail="Missing authentication headers")
    
    # 2. 查找设备
    device = device_repo.get_by_device_id(x_device_id)
    if not device:
        raise HTTPException(401, detail="Invalid device ID")
    
    # 3. 检查设备状态
    if not device.is_active:
        raise HTTPException(403, detail="Device is not active")
    
    # 4. 构建签名字符串
    sign_data = build_signature_data(
        package_id=payload.package_id,
        max_temperature=payload.max_temperature,
        avg_humidity=payload.avg_humidity,
        over_threshold_time=payload.over_threshold_time,
        timestamp=payload.timestamp
    )
    
    # 5. 验证签名
    if not verify_hmac_signature(sign_data, x_signature, device.secret_key):
        raise HTTPException(401, detail="Invalid signature")
    
    # 6. 验证时间戳（防重放攻击）
    current_timestamp = int(datetime.now().timestamp())
    time_diff = abs(current_timestamp - x_timestamp)
    if time_diff > 300:  # 5分钟 = 300秒
        raise HTTPException(401, detail=f"Timestamp out of range (diff: {time_diff}s)")
    
    # 7. 更新最后活跃时间
    device_repo.update_last_seen(x_device_id)
    
    return device
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
    INSERT INTO package_records (package_id, max_temperature, avg_humidity, over_threshold_time, timestamp)
    VALUES (?, ?, ?, ?, ?)
    
    Args:
        data: 包裹上传数据
        
    Returns:
        创建的记录对象（包含自增的 ID）
    """
    db_record = PackageRecord(
        package_id=data.package_id,
        max_temperature=data.max_temperature,
        avg_humidity=data.avg_humidity,
        over_threshold_time=data.over_threshold_time,
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
    """包裹环境监测数据上传请求模型"""
    
    # 包裹ID验证
    package_id: int = Field(
        ...,                    # 必填
        gt=0,                   # 必须大于0
        description="包裹ID，必须为正整数",
        example=1001
    )
    
    # 最高温度验证
    max_temperature: float = Field(
        ...,                    # 必填
        ge=-50.0,              # 大于等于 -50
        le=100.0,              # 小于等于 100
        description="最高温度值(°C)，范围: -50 ~ 100",
        example=28.5
    )
    
    # 平均湿度验证
    avg_humidity: float = Field(
        ...,                    # 必填
        ge=0.0,                # 大于等于 0
        le=100.0,              # 小于等于 100
        description="平均湿度值(%)，范围: 0 ~ 100",
        example=65.2
    )
    
    # 超阈值时间验证
    over_threshold_time: int = Field(
        ...,                    # 必填
        ge=0,                  # 必须大于等于0
        description="超阈值时间(秒)，必须为非负整数",
        example=3600
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

**需求**：在包裹记录中添加"最低温度"字段

**步骤**：

1. **修改数据模型** (`app/models/package.py`)

```python
class PackageRecord(Base):
    __tablename__ = "package_records"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, nullable=False, index=True)
    max_temperature = Column(Float, nullable=False)
    min_temperature = Column(Float, nullable=True)  # ← 新增字段
    avg_humidity = Column(Float, nullable=False)
    over_threshold_time = Column(Integer, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

2. **修改数据验证模型** (`app/schemas/package.py`)

```python
class PackageUploadRequest(BaseModel):
    package_id: int = Field(..., gt=0)
    max_temperature: float = Field(..., ge=-50.0, le=100.0)
    min_temperature: float = Field(None, ge=-50.0, le=100.0)  # ← 新增字段（可选）
    avg_humidity: float = Field(..., ge=0.0, le=100.0)
    over_threshold_time: int = Field(..., ge=0)
    timestamp: int = Field(..., gt=0)
```

3. **创建数据库迁移**

```bash
alembic revision --autogenerate -m "Add min_temperature field"
alembic upgrade head
```

4. **修改业务逻辑**（如需要）

```python
def save_package_data(self, data: PackageUploadRequest):
    # 可以添加温度范围检查逻辑
    if data.min_temperature and data.max_temperature:
        temp_range = data.max_temperature - data.min_temperature
        if temp_range > 20:
            logger.warning(f"Large temperature range: {temp_range}°C")
    
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
  `max_temperature` FLOAT NOT NULL COMMENT '最高温度(°C)',
  `avg_humidity` FLOAT NOT NULL COMMENT '平均湿度(%)',
  `over_threshold_time` INT NOT NULL COMMENT '超阈值时间(秒)',
  `timestamp` BIGINT NOT NULL COMMENT 'Unix时间戳',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  
  INDEX `idx_package_timestamp` (`package_id`, `timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='包裹环境监测记录表';

CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
  `username` VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
  `email` VARCHAR(100) COMMENT '邮箱',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  INDEX `idx_username` (`username`),
  INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE `user_packages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '关联ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `package_id` INT NOT NULL COMMENT '包裹ID',
  `package_name` VARCHAR(100) COMMENT '包裹名称',
  `description` VARCHAR(500) COMMENT '包裹描述',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_package_id` (`package_id`),
  UNIQUE KEY `uk_user_package` (`user_id`, `package_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户包裹关联表';

CREATE TABLE `devices` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '设备ID',
  `device_id` VARCHAR(100) UNIQUE NOT NULL COMMENT '设备唯一标识',
  `device_name` VARCHAR(200) COMMENT '设备名称',
  `description` VARCHAR(500) COMMENT '设备描述',
  `secret_key` VARCHAR(255) NOT NULL COMMENT '设备密钥（HMAC签名用）',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  `last_seen` DATETIME COMMENT '最后活跃时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  INDEX `idx_device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';
```

### 索引说明

- **package_records.idx_package_timestamp**: 复合索引，优化按包裹ID和时间戳查询的性能
- **users.idx_username**: 用于快速查找用户（登录时使用）
- **user_packages.uk_user_package**: 唯一索引，确保每个用户对每个包裹只有一条绑定记录
- **devices.idx_device_id**: 用于快速查找设备（设备认证时使用）

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

---

## 🔐 认证与授权系统

### 用户认证（JWT）

**位置**: `app/utils/auth.py`

系统使用 JWT (JSON Web Token) 进行用户认证：

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT Token
    
    Args:
        data: 用户数据（user_id, username）
        expires_delta: Token过期时间（默认7天）
        
    Returns:
        JWT Token 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### 设备认证（HMAC-SHA256）

**位置**: `app/utils/security.py`

ESP32设备使用 HMAC-SHA256 签名进行认证：

```python
def build_signature_data(
    package_id: int,
    max_temperature: float,
    avg_humidity: float,
    over_threshold_time: int,
    timestamp: int
) -> str:
    """
    构建签名字符串
    
    格式：package_id={id}&max_temperature={temp}&avg_humidity={hum}&over_threshold_time={time}&timestamp={ts}
    """
    return (
        f"package_id={package_id}&max_temperature={max_temperature}"
        f"&avg_humidity={avg_humidity}&over_threshold_time={over_threshold_time}"
        f"&timestamp={timestamp}"
    )

def verify_hmac_signature(sign_data: str, signature: str, secret_key: str) -> bool:
    """
    验证 HMAC-SHA256 签名
    
    Args:
        sign_data: 签名字符串
        signature: 客户端提供的签名（十六进制）
        secret_key: 设备密钥
        
    Returns:
        True 如果签名有效，否则 False
    """
    expected_signature = hmac.new(
        secret_key.encode(),
        sign_data.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
```

### 权限控制

**位置**: `app/api/v1/endpoints/package.py`

用户只能查看自己绑定的包裹数据：

```python
# 检查包裹所有权
if not user_package_repo.check_package_ownership(current_user.user_id, package_id):
    raise HTTPException(403, detail="Access denied")
```

---

## 📊 数据模型说明

### PackageRecord（包裹记录）

每条记录代表包裹到达一个站点后的环境监测数据：

- `max_temperature`: 该站点期间的最高温度
- `avg_humidity`: 该站点期间的平均湿度
- `over_threshold_time`: 温度超过阈值的时间（秒）
- `timestamp`: 记录时间戳

### UserPackage（用户包裹关联）

用于管理用户与包裹的绑定关系：

- 一个用户可以绑定多个包裹
- 一个包裹可以被多个用户绑定
- 通过 `is_active` 字段控制绑定状态

### Device（设备）

ESP32设备信息：

- `device_id`: 设备唯一标识
- `secret_key`: 用于HMAC签名的密钥（只在创建时返回一次）
- `is_active`: 设备是否激活（未激活的设备无法上传数据）

---

**文档版本**: 2.0.0  
**最后更新**: 2024-12-02  
**维护人员**: 后端开发团队
