# ESP32 数据上传安全方案开发文档

## 📋 文档概述

本文档详细说明基于 **device_id + HMAC 签名** 的安全方案实现，包括后端和 ESP32 端的完整开发规划。

**方案特点**：
- ✅ 设备身份认证（通过 device_id）
- ✅ 数据完整性保护（通过 HMAC 签名）
- ✅ 防重放攻击（时间戳验证）
- ✅ 实现简单，性能优秀

---

## 🏗️ 架构设计

### 安全流程

```
┌─────────────┐                    ┌─────────────┐
│   ESP32     │                    │   后端      │
└──────┬──────┘                    └──────┬──────┘
       │                                   │
       │ 1. 构建请求数据                    │
       │    package_id, temperature, ...   │
       │                                   │
       │ 2. 构建签名字符串                  │
       │    "package_id=1001&temp=28.5..." │
       │                                   │
       │ 3. 使用 Secret Key 生成 HMAC 签名  │
       │    signature = HMAC-SHA256(...)   │
       │                                   │
       │ 4. 发送请求                        │
       │    POST /api/v1/upload            │
       │    X-Device-ID: ESP32-001         │
       │    X-Signature: abc123...         │
       │    X-Timestamp: 1700000000        │
       │    Body: {...}                    │
       ├──────────────────────────────────>│
       │                                   │
       │                                   │ 5. 通过 device_id 查找设备
       │                                   │    device = get_device("ESP32-001")
       │                                   │
       │                                   │ 6. 检查设备状态
       │                                   │    if not device.is_active: reject
       │                                   │
       │                                   │ 7. 重新计算签名
       │                                   │    expected = HMAC(data, device.secret_key)
       │                                   │
       │                                   │ 8. 验证签名
       │                                   │    if signature != expected: reject
       │                                   │
       │                                   │ 9. 验证时间戳
       │                                   │    if timestamp invalid: reject
       │                                   │
       │                                   │ 10. 处理数据
       │                                   │     save_to_database()
       │                                   │
       │ 11. 返回结果                       │
       │     {status: "success", ...}     │
       │<──────────────────────────────────┤
       │                                   │
```

---

## 🗄️ 数据库设计

### 设备表（devices）

```sql
CREATE TABLE `devices` (
    `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    `device_id` VARCHAR(50) UNIQUE NOT NULL COMMENT '设备唯一标识（如：ESP32-001）',
    `device_name` VARCHAR(100) NULL COMMENT '设备名称（可选）',
    `secret_key` VARCHAR(64) NOT NULL COMMENT 'HMAC 签名密钥（保密）',
    `is_active` BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否激活',
    `description` TEXT NULL COMMENT '设备描述',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新时间',
    `last_seen` TIMESTAMP NULL COMMENT '最后活跃时间',
    
    INDEX `idx_device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ESP32 设备表';
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `device_id` | VARCHAR(50) | 设备唯一标识，用于识别设备 | `ESP32-001` |
| `secret_key` | VARCHAR(64) | HMAC 签名密钥（64字符十六进制） | `abc123def456...` |
| `is_active` | BOOLEAN | 是否激活，False 时拒绝所有请求 | `true` |
| `last_seen` | TIMESTAMP | 最后活跃时间，用于监控设备状态 | `2024-12-06 15:30:00` |

---

## 🔧 后端开发规划

### 1. 数据模型层（Models）

#### 文件：`app/models/device.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Device(Base):
    """ESP32 设备模型"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, nullable=False, index=True)
    device_name = Column(String(100), nullable=True)
    secret_key = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_seen = Column(DateTime, nullable=True)
```

**开发任务**：
- [ ] 创建 `app/models/device.py`
- [ ] 在 `app/models/__init__.py` 中导出 Device
- [ ] 创建数据库迁移脚本

---

### 2. 安全工具层（Utils）

#### 文件：`app/utils/security.py`

**功能**：
1. HMAC 签名生成和验证
2. 密钥生成
3. 签名字符串构建

```python
import hmac
import hashlib
import secrets
from typing import Optional

def generate_secret_key() -> str:
    """生成 32 字节的 Secret Key（64字符十六进制）"""
    return secrets.token_hex(32)

def build_signature_data(
    package_id: int,
    max_temperature: float,
    avg_humidity: float,
    over_threshold_time: int,
    timestamp: int
) -> str:
    """
    构建用于签名的数据字符串
    按照固定顺序拼接所有字段
    """
    return (
        f"package_id={package_id}&"
        f"max_temperature={max_temperature:.2f}&"
        f"avg_humidity={avg_humidity:.2f}&"
        f"over_threshold_time={over_threshold_time}&"
        f"timestamp={timestamp}"
    )

def generate_hmac_signature(data: str, secret_key: str) -> str:
    """生成 HMAC-SHA256 签名"""
    signature = hmac.new(
        secret_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_hmac_signature(data: str, signature: str, secret_key: str) -> bool:
    """验证 HMAC 签名（使用安全比较，防止时序攻击）"""
    expected_signature = generate_hmac_signature(data, secret_key)
    return hmac.compare_digest(expected_signature, signature)
```

**开发任务**：
- [ ] 创建 `app/utils/security.py`
- [ ] 实现密钥生成函数
- [ ] 实现签名生成和验证函数
- [ ] 编写单元测试

---

### 3. 数据访问层（Repository）

#### 文件：`app/repositories/device_repository.py`

```python
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.device import Device
from datetime import datetime

class DeviceRepository:
    """设备数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """根据 device_id 获取设备"""
        return self.db.query(Device).filter(
            Device.device_id == device_id
        ).first()
    
    def create(self, device_id: str, device_name: str = None, 
               secret_key: str = None, description: str = None) -> Device:
        """创建设备"""
        device = Device(
            device_id=device_id,
            device_name=device_name,
            secret_key=secret_key,
            description=description
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device
    
    def update_last_seen(self, device_id: str) -> bool:
        """更新设备最后活跃时间"""
        device = self.get_by_device_id(device_id)
        if device:
            device.last_seen = datetime.now()
            self.db.commit()
            return True
        return False
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Device]:
        """获取所有设备（分页）"""
        return self.db.query(Device).offset(skip).limit(limit).all()
    
    def activate(self, device_id: str) -> bool:
        """激活设备"""
        device = self.get_by_device_id(device_id)
        if device:
            device.is_active = True
            self.db.commit()
            return True
        return False
    
    def deactivate(self, device_id: str) -> bool:
        """停用设备"""
        device = self.get_by_device_id(device_id)
        if device:
            device.is_active = False
            self.db.commit()
            return True
        return False
```

**开发任务**：
- [ ] 创建 `app/repositories/device_repository.py`
- [ ] 实现设备 CRUD 操作
- [ ] 在 `app/repositories/__init__.py` 中导出

---

### 4. 认证依赖（Dependencies）

#### 文件：`app/api/deps.py`（新增函数）

```python
from fastapi import Header, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.device_repository import DeviceRepository
from app.utils.security import (
    build_signature_data,
    verify_hmac_signature
)
from app.schemas.package import PackageUploadRequest
from loguru import logger
from datetime import datetime

def get_device_repository(db: Session = Depends(get_db)) -> DeviceRepository:
    """获取设备仓库实例"""
    return DeviceRepository(db)

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
    5. 验证 HMAC 签名
    6. 验证时间戳（防重放）
    7. 更新设备最后活跃时间
    """
    # 1. 检查请求头
    if not x_device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Device-ID header"
        )
    
    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Signature header"
        )
    
    if not x_timestamp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Timestamp header"
        )
    
    # 2. 查找设备
    device = device_repo.get_by_device_id(x_device_id)
    if not device:
        logger.warning(f"Unknown device attempted access: {x_device_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device ID"
        )
    
    # 3. 检查设备状态
    if not device.is_active:
        logger.warning(f"Inactive device attempted access: {x_device_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device is not active"
        )
    
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
        logger.warning(f"Invalid signature from device: {x_device_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # 6. 验证时间戳（防重放攻击）
    current_timestamp = int(datetime.now().timestamp())
    time_diff = abs(current_timestamp - x_timestamp)
    
    # 允许 5 分钟的时间误差
    if time_diff > 300:  # 5分钟 = 300秒
        logger.warning(
            f"Timestamp out of range from device {x_device_id}: "
            f"diff={time_diff}s"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Timestamp out of range (diff: {time_diff}s)"
        )
    
    # 7. 更新最后活跃时间
    device_repo.update_last_seen(x_device_id)
    
    logger.info(f"Device authenticated: {x_device_id}")
    return device
```

**开发任务**：
- [ ] 在 `app/api/deps.py` 中添加设备认证函数
- [ ] 实现完整的验证流程
- [ ] 添加详细的错误日志

---

### 5. API 接口层

#### 5.1 更新上传接口

**文件**：`app/api/v1/endpoints/package.py`

```python
@router.post("/upload", response_model=Dict[str, Any], tags=["Package"])
async def upload_package_data(
    payload: PackageUploadRequest,
    device: Device = Depends(verify_device_authentication),  # 添加认证依赖
    service: PackageService = Depends(get_package_service)
):
    """
    接收 ESP32 上传的 RFID 包裹数据（需要设备认证）
    
    请求头要求：
    - X-Device-ID: 设备标识
    - X-Signature: HMAC 签名
    - X-Timestamp: 时间戳
    """
    try:
        result = service.save_package_data(payload)
        logger.info(f"Data uploaded by device: {device.device_id}")
        return result
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

**开发任务**：
- [ ] 更新 `upload_package_data` 函数
- [ ] 添加设备认证依赖
- [ ] 更新 API 文档注释

---

#### 5.2 设备管理接口

**文件**：`app/api/v1/endpoints/device.py`（新建）

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user, get_device_repository
from app.repositories.device_repository import DeviceRepository
from app.utils.security import generate_secret_key
from app.schemas.device import (
    DeviceCreateRequest,
    DeviceResponse,
    DeviceListResponse
)
from app.schemas.user import TokenData

router = APIRouter()

@router.post("/devices", response_model=DeviceResponse, tags=["Device"])
async def create_device(
    device_data: DeviceCreateRequest,
    current_user: TokenData = Depends(get_current_user),  # 需要管理员权限
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """
    注册新设备（需要管理员权限）
    
    自动生成 secret_key
    """
    # 检查设备是否已存在
    existing = device_repo.get_by_device_id(device_data.device_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device {device_data.device_id} already exists"
        )
    
    # 生成密钥
    secret_key = generate_secret_key()
    
    # 创建设备
    device = device_repo.create(
        device_id=device_data.device_id,
        device_name=device_data.device_name,
        secret_key=secret_key,
        description=device_data.description
    )
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        is_active=device.is_active,
        created_at=device.created_at,
        last_seen=device.last_seen,
        secret_key=secret_key  # 只在创建时返回一次
    )

@router.get("/devices", response_model=DeviceListResponse, tags=["Device"])
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user),
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """获取设备列表（需要登录）"""
    devices = device_repo.get_all(skip=skip, limit=limit)
    return DeviceListResponse(
        total=len(devices),
        devices=[DeviceResponse.from_orm(d) for d in devices]
    )

@router.post("/devices/{device_id}/activate", tags=["Device"])
async def activate_device(
    device_id: str,
    current_user: TokenData = Depends(get_current_user),
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """激活设备"""
    if device_repo.activate(device_id):
        return {"status": "success", "message": f"Device {device_id} activated"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/devices/{device_id}/deactivate", tags=["Device"])
async def deactivate_device(
    device_id: str,
    current_user: TokenData = Depends(get_current_user),
    device_repo: DeviceRepository = Depends(get_device_repository)
):
    """停用设备"""
    if device_repo.deactivate(device_id):
        return {"status": "success", "message": f"Device {device_id} deactivated"}
    raise HTTPException(status_code=404, detail="Device not found")
```

**开发任务**：
- [ ] 创建 `app/api/v1/endpoints/device.py`
- [ ] 实现设备注册接口
- [ ] 实现设备列表接口
- [ ] 实现激活/停用接口
- [ ] 在路由中注册设备接口

---

### 6. Schema 层

#### 文件：`app/schemas/device.py`（新建）

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class DeviceCreateRequest(BaseModel):
    """创建设备请求"""
    device_id: str = Field(..., min_length=1, max_length=50, description="设备唯一标识")
    device_name: Optional[str] = Field(None, max_length=100, description="设备名称")
    description: Optional[str] = Field(None, description="设备描述")

class DeviceResponse(BaseModel):
    """设备响应"""
    id: int
    device_id: str
    device_name: Optional[str]
    is_active: bool
    created_at: datetime
    last_seen: Optional[datetime]
    secret_key: Optional[str] = None  # 只在创建时返回
    
    class Config:
        from_attributes = True

class DeviceListResponse(BaseModel):
    """设备列表响应"""
    total: int
    devices: List[DeviceResponse]
```

**开发任务**：
- [ ] 创建 `app/schemas/device.py`
- [ ] 定义设备相关的 Schema

---

## 📱 ESP32 端开发规划

### 1. HMAC-SHA256 实现

#### 方案 A：使用 mbedTLS（推荐）

ESP32 自带 mbedTLS 库，可以直接使用。

```cpp
#include "mbedtls/md.h"

/**
 * 计算 HMAC-SHA256 签名
 * 
 * @param data 要签名的数据字符串
 * @param key 密钥
 * @param output 输出缓冲区（至少 65 字节，用于存储十六进制字符串）
 * @return true 成功, false 失败
 */
bool hmacSHA256(const char* data, const char* key, char* output) {
    mbedtls_md_context_t ctx;
    const mbedtls_md_info_t *md_info;
    unsigned char hmac_output[32];  // SHA256 输出 32 字节
    
    // 获取 MD5 信息（实际使用 SHA256）
    md_info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    if (md_info == NULL) {
        return false;
    }
    
    // 初始化上下文
    mbedtls_md_init(&ctx);
    if (mbedtls_md_setup(&ctx, md_info, 1) != 0) {  // 1 = HMAC
        mbedtls_md_free(&ctx);
        return false;
    }
    
    // 计算 HMAC
    if (mbedtls_md_hmac_starts(&ctx, (const unsigned char*)key, strlen(key)) != 0 ||
        mbedtls_md_hmac_update(&ctx, (const unsigned char*)data, strlen(data)) != 0 ||
        mbedtls_md_hmac_finish(&ctx, hmac_output) != 0) {
        mbedtls_md_free(&ctx);
        return false;
    }
    
    // 转换为十六进制字符串
    for (int i = 0; i < 32; i++) {
        sprintf(output + i * 2, "%02x", hmac_output[i]);
    }
    output[64] = '\0';
    
    mbedtls_md_free(&ctx);
    return true;
}
```

#### 方案 B：使用第三方库

如果 mbedTLS 不可用，可以使用 `Crypto` 库。

---

### 2. 密钥存储

#### 使用 NVS（非易失性存储）

```cpp
#include <Preferences.h>

Preferences preferences;

// 设备配置
const char* DEVICE_ID = "ESP32-001";
const char* NVS_NAMESPACE = "device_config";
const char* NVS_KEY_SECRET = "secret_key";

/**
 * 从 NVS 读取 Secret Key
 */
String readSecretKey() {
    preferences.begin(NVS_NAMESPACE, true);  // 只读模式
    String secretKey = preferences.getString(NVS_KEY_SECRET, "");
    preferences.end();
    return secretKey;
}

/**
 * 保存 Secret Key 到 NVS
 */
void saveSecretKey(const char* secretKey) {
    preferences.begin(NVS_NAMESPACE, false);  // 读写模式
    preferences.putString(NVS_KEY_SECRET, secretKey);
    preferences.end();
}

/**
 * 初始化设备配置
 * 首次运行时需要从服务器获取并保存 Secret Key
 */
void initDeviceConfig() {
    String secretKey = readSecretKey();
    if (secretKey.length() == 0) {
        Serial.println("⚠️ Secret Key not found, need to register device");
        // TODO: 实现设备注册流程
    } else {
        Serial.println("✅ Device config loaded");
    }
}
```

---

### 3. 签名生成函数

```cpp
/**
 * 构建签名字符串
 * 格式：package_id=1001&max_temperature=28.50&avg_humidity=65.20&over_threshold_time=3600&timestamp=1700000000
 */
String buildSignatureData(
    uint32_t packageId,
    float maxTemperature,
    float avgHumidity,
    uint32_t overThresholdTime,
    uint64_t timestamp
) {
    char buffer[256];
    snprintf(
        buffer, sizeof(buffer),
        "package_id=%u&max_temperature=%.2f&avg_humidity=%.2f&over_threshold_time=%u&timestamp=%llu",
        packageId,
        maxTemperature,
        avgHumidity,
        overThresholdTime,
        timestamp
    );
    return String(buffer);
}

/**
 * 生成 HMAC 签名
 */
String generateSignature(
    uint32_t packageId,
    float maxTemperature,
    float avgHumidity,
    uint32_t overThresholdTime,
    uint64_t timestamp,
    const char* secretKey
) {
    // 1. 构建签名字符串
    String signData = buildSignatureData(
        packageId, maxTemperature, avgHumidity, 
        overThresholdTime, timestamp
    );
    
    // 2. 计算 HMAC-SHA256
    char signature[65];
    if (!hmacSHA256(signData.c_str(), secretKey, signature)) {
        Serial.println("❌ HMAC calculation failed");
        return "";
    }
    
    return String(signature);
}
```

---

### 4. HTTP 请求更新

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// 服务器配置
const char* SERVER_URL = "http://192.168.1.100:8000/api/v1/upload";
const char* DEVICE_ID = "ESP32-001";

/**
 * 上传包裹数据（带认证）
 */
bool uploadPackageData(
    uint32_t packageId,
    float maxTemperature,
    float avgHumidity,
    uint32_t overThresholdTime,
    uint64_t timestamp
) {
    // 检查 WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi not connected");
        return false;
    }
    
    // 读取 Secret Key
    String secretKey = readSecretKey();
    if (secretKey.length() == 0) {
        Serial.println("❌ Secret Key not found");
        return false;
    }
    
    // 生成签名
    String signature = generateSignature(
        packageId, maxTemperature, avgHumidity,
        overThresholdTime, timestamp,
        secretKey.c_str()
    );
    
    if (signature.length() == 0) {
        Serial.println("❌ Signature generation failed");
        return false;
    }
    
    // 构建 JSON 数据
    StaticJsonDocument<200> doc;
    doc["package_id"] = packageId;
    doc["max_temperature"] = maxTemperature;
    doc["avg_humidity"] = avgHumidity;
    doc["over_threshold_time"] = overThresholdTime;
    doc["timestamp"] = timestamp;
    
    String requestBody;
    serializeJson(doc, requestBody);
    
    // 发送 HTTP 请求
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-ID", DEVICE_ID);
    http.addHeader("X-Signature", signature);
    http.addHeader("X-Timestamp", String(timestamp));
    http.setTimeout(5000);
    
    Serial.println("📤 Uploading data...");
    Serial.println("  Device ID: " + String(DEVICE_ID));
    Serial.println("  Signature: " + signature.substring(0, 16) + "...");
    
    int httpCode = http.POST(requestBody);
    
    bool success = false;
    if (httpCode == 200) {
        String response = http.getString();
        Serial.println("✅ Upload successful: " + response);
        success = true;
    } else if (httpCode == 401) {
        Serial.println("❌ Authentication failed");
        String response = http.getString();
        Serial.println("  Response: " + response);
    } else if (httpCode > 0) {
        Serial.printf("❌ HTTP Error %d: %s\n", httpCode, http.getString().c_str());
    } else {
        Serial.printf("❌ Connection error: %s\n", http.errorToString(httpCode).c_str());
    }
    
    http.end();
    return success;
}
```

---

### 5. 完整示例代码

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include "mbedtls/md.h"

// ==================== 配置 ====================
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.100:8000/api/v1/upload";
const char* DEVICE_ID = "ESP32-001";

// ==================== 全局变量 ====================
Preferences preferences;

// ==================== 函数声明 ====================
void initWiFi();
String readSecretKey();
void saveSecretKey(const char* secretKey);
bool hmacSHA256(const char* data, const char* key, char* output);
String buildSignatureData(uint32_t pkgId, float maxTemp, float avgHum, 
                         uint32_t overTime, uint64_t ts);
String generateSignature(uint32_t pkgId, float maxTemp, float avgHum,
                         uint32_t overTime, uint64_t ts, const char* secretKey);
bool uploadPackageData(uint32_t pkgId, float maxTemp, float avgHum,
                      uint32_t overTime, uint64_t ts);

// ==================== Setup ====================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\n=================================");
    Serial.println("ESP32 Secure Data Uploader");
    Serial.println("=================================\n");
    
    // 初始化 WiFi
    initWiFi();
    
    // 检查 Secret Key
    String secretKey = readSecretKey();
    if (secretKey.length() == 0) {
        Serial.println("⚠️ Secret Key not found!");
        Serial.println("Please register device first and save Secret Key");
        // TODO: 实现设备注册流程
    } else {
        Serial.println("✅ Device config loaded");
        Serial.println("  Device ID: " + String(DEVICE_ID));
    }
    
    Serial.println("\n🚀 System ready!\n");
}

// ==================== Loop ====================
void loop() {
    // 示例：上传测试数据
    uint32_t packageId = 1001;
    float maxTemp = 28.5;
    float avgHumidity = 65.2;
    uint32_t overTime = 3600;
    uint64_t timestamp = (uint64_t)time(nullptr);
    
    if (uploadPackageData(packageId, maxTemp, avgHumidity, overTime, timestamp)) {
        Serial.println("✅ Data uploaded successfully");
    } else {
        Serial.println("❌ Upload failed");
    }
    
    delay(10000);  // 10秒后再次上传
}

// ==================== WiFi 函数 ====================
void initWiFi() {
    Serial.print("📶 Connecting to WiFi");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int retry = 0;
    while (WiFi.status() != WL_CONNECTED && retry < 40) {
        delay(500);
        Serial.print(".");
        retry++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi connected!");
        Serial.print("  IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n❌ WiFi connection failed!");
    }
}

// ==================== NVS 函数 ====================
String readSecretKey() {
    preferences.begin("device_config", true);
    String key = preferences.getString("secret_key", "");
    preferences.end();
    return key;
}

void saveSecretKey(const char* secretKey) {
    preferences.begin("device_config", false);
    preferences.putString("secret_key", secretKey);
    preferences.end();
    Serial.println("✅ Secret Key saved to NVS");
}

// ==================== HMAC 函数 ====================
bool hmacSHA256(const char* data, const char* key, char* output) {
    mbedtls_md_context_t ctx;
    const mbedtls_md_info_t *md_info;
    unsigned char hmac_output[32];
    
    md_info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    if (md_info == NULL) return false;
    
    mbedtls_md_init(&ctx);
    if (mbedtls_md_setup(&ctx, md_info, 1) != 0) {
        mbedtls_md_free(&ctx);
        return false;
    }
    
    if (mbedtls_md_hmac_starts(&ctx, (const unsigned char*)key, strlen(key)) != 0 ||
        mbedtls_md_hmac_update(&ctx, (const unsigned char*)data, strlen(data)) != 0 ||
        mbedtls_md_hmac_finish(&ctx, hmac_output) != 0) {
        mbedtls_md_free(&ctx);
        return false;
    }
    
    for (int i = 0; i < 32; i++) {
        sprintf(output + i * 2, "%02x", hmac_output[i]);
    }
    output[64] = '\0';
    
    mbedtls_md_free(&ctx);
    return true;
}

String buildSignatureData(uint32_t pkgId, float maxTemp, float avgHum,
                         uint32_t overTime, uint64_t ts) {
    char buffer[256];
    snprintf(buffer, sizeof(buffer),
        "package_id=%u&max_temperature=%.2f&avg_humidity=%.2f&over_threshold_time=%u&timestamp=%llu",
        pkgId, maxTemp, avgHum, overTime, ts);
    return String(buffer);
}

String generateSignature(uint32_t pkgId, float maxTemp, float avgHum,
                         uint32_t overTime, uint64_t ts, const char* secretKey) {
    String signData = buildSignatureData(pkgId, maxTemp, avgHum, overTime, ts);
    char signature[65];
    if (!hmacSHA256(signData.c_str(), secretKey, signature)) {
        return "";
    }
    return String(signature);
}

// ==================== HTTP 上传函数 ====================
bool uploadPackageData(uint32_t pkgId, float maxTemp, float avgHum,
                      uint32_t overTime, uint64_t ts) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi not connected");
        return false;
    }
    
    String secretKey = readSecretKey();
    if (secretKey.length() == 0) {
        Serial.println("❌ Secret Key not found");
        return false;
    }
    
    String signature = generateSignature(pkgId, maxTemp, avgHum, overTime, ts, secretKey.c_str());
    if (signature.length() == 0) {
        Serial.println("❌ Signature generation failed");
        return false;
    }
    
    StaticJsonDocument<200> doc;
    doc["package_id"] = pkgId;
    doc["max_temperature"] = maxTemp;
    doc["avg_humidity"] = avgHum;
    doc["over_threshold_time"] = overTime;
    doc["timestamp"] = ts;
    
    String requestBody;
    serializeJson(doc, requestBody);
    
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-ID", DEVICE_ID);
    http.addHeader("X-Signature", signature);
    http.addHeader("X-Timestamp", String(ts));
    http.setTimeout(5000);
    
    Serial.println("📤 Uploading...");
    int httpCode = http.POST(requestBody);
    
    bool success = (httpCode == 200);
    if (success) {
        Serial.println("✅ Success: " + http.getString());
    } else {
        Serial.printf("❌ Error %d: %s\n", httpCode, http.getString().c_str());
    }
    
    http.end();
    return success;
}
```

---

## 🧪 测试计划

### 后端测试

1. **单元测试**
   - [ ] HMAC 签名生成和验证
   - [ ] 签名字符串构建
   - [ ] 设备仓库 CRUD 操作

2. **集成测试**
   - [ ] 设备认证流程
   - [ ] 签名验证流程
   - [ ] 时间戳验证
   - [ ] 设备激活/停用

3. **API 测试**
   - [ ] 正常上传（有效签名）
   - [ ] 无效设备 ID
   - [ ] 无效签名
   - [ ] 过期时间戳
   - [ ] 停用设备访问

### ESP32 测试

1. **功能测试**
   - [ ] HMAC 签名生成
   - [ ] HTTP 请求发送
   - [ ] 密钥存储和读取

2. **集成测试**
   - [ ] 完整上传流程
   - [ ] 错误处理
   - [ ] 重试机制

---

## 📝 开发检查清单

### 后端开发

- [ ] 创建 Device 模型
- [ ] 创建数据库迁移脚本
- [ ] 实现安全工具函数
- [ ] 实现设备仓库
- [ ] 实现设备认证依赖
- [ ] 更新上传接口
- [ ] 创建设备管理接口
- [ ] 创建 Schema
- [ ] 编写单元测试
- [ ] 更新 API 文档

### ESP32 开发

- [ ] 实现 HMAC-SHA256 函数
- [ ] 实现密钥存储（NVS）
- [ ] 实现签名生成函数
- [ ] 更新 HTTP 请求函数
- [ ] 添加错误处理
- [ ] 测试完整流程

---

## 🔒 安全注意事项

1. **Secret Key 保护**
   - 不要在代码中硬编码 Secret Key
   - 使用 NVS 安全存储
   - 首次部署时通过安全渠道传输密钥

2. **HTTPS（生产环境）**
   - 开发环境可以使用 HTTP
   - 生产环境必须使用 HTTPS
   - 配置 SSL 证书

3. **时间同步**
   - ESP32 必须使用 NTP 同步时间
   - 时间戳验证允许 5 分钟误差

4. **密钥轮换**
   - 定期更换 Secret Key
   - 实现密钥重置接口

5. **日志安全**
   - 不要在日志中输出 Secret Key
   - 可以输出 device_id 和签名的前几位

---

## 📚 参考资料

- [HMAC-SHA256 算法](https://en.wikipedia.org/wiki/HMAC)
- [ESP32 mbedTLS 文档](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/protocols/mbedtls.html)
- [FastAPI 安全文档](https://fastapi.tiangolo.com/tutorial/security/)

---

**文档版本**: 1.0.0  
**最后更新**: 2024-12-06  
**维护人员**: 后端开发团队

