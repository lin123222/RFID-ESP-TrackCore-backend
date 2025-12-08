# RFID包裹监控系统 API接口文档

## 📋 基础信息

- **服务器地址**: `http://localhost:8000`
- **API版本**: `v1`
- **基础路径**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 🔐 认证说明

系统支持两种认证方式：

### 1. 用户认证（JWT Token）
除了健康检查、用户注册/登录接口和ESP32设备上传接口外，所有接口都需要在请求头中携带JWT Token：

```http
Authorization: Bearer {your_jwt_token}
```

### 2. 设备认证（HMAC-SHA256签名）
ESP32设备上传数据需要使用设备认证，需要在请求头中携带：
- `X-Device-ID`: 设备唯一标识
- `X-Signature`: HMAC-SHA256签名
- `X-Timestamp`: Unix时间戳（秒）

## 📡 通用响应格式

### 成功响应
```json
{
    "status": "success",
    "message": "操作成功",
    "data": {
        // 具体数据
    }
}
```

### 错误响应
```json
{
    "status": "error",
    "message": "错误信息",
    "detail": "详细错误描述"
}
```

## 🏥 1. 健康检查

### 1.1 系统健康检查
- **接口**: `GET /api/v1/health`
- **描述**: 检查系统和数据库连接状态
- **认证**: 无需认证

**响应示例**:
```json
{
    "status": "healthy",
    "database": "connected",
    "app_name": "RFID Cold Chain Monitor",
    "version": "v1"
}
```

## 🔑 2. 用户认证

### 2.1 用户注册
- **接口**: `POST /api/v1/auth/register`
- **描述**: 新用户注册
- **认证**: 无需认证

**请求参数**:
```json
{
    "username": "user123",           // 必填，用户名，3-50字符
    "email": "user@example.com",     // 可选，邮箱
    "password": "password123"        // 必填，密码，6-50字符
}
```

**响应示例**:
```json
{
    "status": "success",
    "message": "注册成功",
    "data": {
        "id": 1,
        "username": "user123",
        "email": "user@example.com",
        "is_active": true,
        "created_at": "2024-12-02T15:30:00Z",
        "updated_at": "2024-12-02T15:30:00Z"
    }
}
```

### 2.2 用户登录
- **接口**: `POST /api/v1/auth/login`
- **描述**: 用户登录获取Token
- **认证**: 无需认证

**请求参数**:
```json
{
    "username": "user123",      // 必填，用户名
    "password": "password123"   // 必填，密码
}
```

**响应示例**:
```json
{
    "status": "success",
    "message": "登录成功",
    "data": {
        "user_id": 1,
        "username": "user123",
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "expires_in": 604800,
        "token_type": "bearer"
    }
}
```

### 2.3 获取当前用户信息
- **接口**: `GET /api/v1/auth/me`
- **描述**: 获取当前登录用户的信息
- **认证**: 需要Token

**响应示例**:
```json
{
    "status": "success",
    "message": "获取成功",
    "data": {
        "id": 1,
        "username": "user123",
        "email": "user@example.com",
        "is_active": true,
        "created_at": "2024-12-02T15:30:00Z",
        "updated_at": "2024-12-02T15:30:00Z"
    }
}
```

### 2.4 更新用户信息
- **接口**: `PUT /api/v1/auth/me`
- **描述**: 更新当前用户信息
- **认证**: 需要Token

**请求参数**:
```json
{
    "username": "newusername",        // 可选，新用户名，3-50字符
    "email": "newemail@example.com"   // 可选，新邮箱
}
```

### 2.5 修改密码
- **接口**: `POST /api/v1/auth/change-password`
- **描述**: 修改用户密码
- **认证**: 需要Token

**请求参数**:
```json
{
    "old_password": "oldpassword123",  // 必填，旧密码
    "new_password": "newpassword123"   // 必填，新密码，6-50字符
}
```

## 📦 3. 包裹管理

### 3.1 绑定包裹
- **接口**: `POST /api/v1/packages/bind`
- **描述**: 用户绑定一个包裹
- **认证**: 需要Token

**请求参数**:
```json
{
    "package_id": 1001,                    // 必填，包裹ID
    "package_name": "重要文件包裹",        // 可选，包裹名称
    "description": "包含重要合同文件"      // 可选，包裹描述
}
```

**响应示例**:
```json
{
    "status": "success",
    "message": "包裹绑定成功",
    "data": {
        "id": 1,
        "package_id": 1001,
        "package_name": "重要文件包裹",
        "description": "包含重要合同文件",
        "is_active": true,
        "created_at": "2024-12-02T15:30:00Z",
        "updated_at": "2024-12-02T15:30:00Z",
        "latest_temperature": 24.5,
        "latest_humidity": 65.2,
        "last_update": "2024-12-02T15:25:00Z",
        "record_count": 150
    }
}
```

### 3.2 解绑包裹
- **接口**: `DELETE /api/v1/packages/{package_id}`
- **描述**: 解绑指定包裹
- **认证**: 需要Token

**路径参数**:
- `package_id`: 包裹ID

**响应示例**:
```json
{
    "status": "success",
    "message": "包裹解绑成功",
    "data": true
}
```

### 3.3 获取用户包裹列表
- **接口**: `GET /api/v1/packages`
- **描述**: 获取当前用户绑定的所有包裹
- **认证**: 需要Token

**查询参数**:
- `page`: 页码，默认1
- `size`: 每页数量，默认10，最大100

**请求示例**:
```
GET /api/v1/packages?page=1&size=10
```

**响应示例**:
```json
{
    "status": "success",
    "message": "获取成功",
    "data": {
        "total": 5,
        "page": 1,
        "size": 10,
        "items": [
            {
                "id": 1,
                "package_id": 1001,
                "package_name": "重要文件包裹",
                "description": "包含重要合同文件",
                "is_active": true,
                "created_at": "2024-12-02T15:30:00Z",
                "updated_at": "2024-12-02T15:30:00Z",
                "latest_temperature": 24.5,
                "latest_humidity": 65.2,
                "last_update": "2024-12-02T15:25:00Z",
                "record_count": 150
            }
        ]
    }
}
```

### 3.4 获取包裹详情
- **接口**: `GET /api/v1/packages/{package_id}`
- **描述**: 获取指定包裹的详细信息
- **认证**: 需要Token

**路径参数**:
- `package_id`: 包裹ID

**响应示例**:
```json
{
    "status": "success",
    "message": "获取成功",
    "data": {
        "id": 1,
        "package_id": 1001,
        "package_name": "重要文件包裹",
        "description": "包含重要合同文件",
        "is_active": true,
        "created_at": "2024-12-02T15:30:00Z",
        "updated_at": "2024-12-02T15:30:00Z",
        "latest_temperature": 24.5,
        "latest_humidity": 65.2,
        "last_update": "2024-12-02T15:25:00Z",
        "record_count": 150
    }
}
```

## 📊 4. 数据查询

### 4.1 获取包裹站点记录 ⭐
- **接口**: `GET /api/v1/packages/{package_id}/records`
- **描述**: 获取包裹在运输过程中到达各个站点后记录的数据
- **认证**: 需要Token
- **权限**: 只能查看已绑定到自己账户的包裹数据

**路径参数**:
- `package_id`: 包裹ID

**查询参数**:
- `limit`: 返回记录数量，默认1000，最大10000
- `offset`: 偏移量（用于分页），默认0

**请求示例**:
```
GET /api/v1/packages/1001/records?limit=100&offset=0
Authorization: Bearer {your_jwt_token}
```

**响应示例**:
```json
{
    "package_id": 1001,
    "total": 150,
    "records": [
        {
            "id": 1,
            "package_id": 1001,
            "max_temperature": 24.5,
            "avg_humidity": 65.2,
            "over_threshold_time": 3600,
            "timestamp": 1701504000,
            "created_at": "2024-12-02T15:25:00Z"
        }
    ]
}
```

**错误响应** (未绑定包裹):
```json
{
    "detail": "Access denied: You don't have permission to view package 1001"
}
```
**状态码**: `403 Forbidden`

**注意事项**:
- 需要先通过 `/api/v1/packages/bind` 接口绑定包裹到账户
- 返回数据按时间倒序排列（最新的在前）
- 每条记录代表包裹到达一个站点后的数据
- 数据包含：最大温度、平均湿度、超阈值时间、时间戳

## 🔧 5. 设备管理

### 5.1 注册设备
- **接口**: `POST /api/v1/devices`
- **描述**: 注册新的ESP32设备
- **认证**: 需要Token（用户登录）

**请求参数**:
```json
{
    "device_id": "ESP32-001",              // 必填，设备唯一标识
    "device_name": "站点1温度传感器",      // 可选，设备名称
    "description": "位于仓库A区"           // 可选，设备描述
}
```

**响应示例**:
```json
{
    "id": 1,
    "device_id": "ESP32-001",
    "device_name": "站点1温度传感器",
    "description": "位于仓库A区",
    "secret_key": "a1b2c3d4e5f6...",      // ⚠️ 只在创建时返回一次，请妥善保管
    "is_active": true,
    "last_seen": null,
    "created_at": "2024-12-02T15:30:00Z",
    "updated_at": "2024-12-02T15:30:00Z"
}
```

**注意事项**:
- `secret_key` 只在设备创建时返回一次，请立即保存
- 如果丢失，需要重新注册设备或联系管理员重置

### 5.2 获取设备列表
- **接口**: `GET /api/v1/devices`
- **描述**: 获取所有已注册的设备列表
- **认证**: 需要Token

**查询参数**:
- `page`: 页码，默认1
- `size`: 每页数量，默认10，最大100

**响应示例**:
```json
{
    "total": 5,
    "page": 1,
    "size": 10,
    "items": [
        {
            "id": 1,
            "device_id": "ESP32-001",
            "device_name": "站点1温度传感器",
            "is_active": true,
            "last_seen": "2024-12-02T15:25:00Z",
            "created_at": "2024-12-02T15:30:00Z"
        }
    ]
}
```

### 5.3 获取设备详情
- **接口**: `GET /api/v1/devices/{device_id}`
- **描述**: 获取指定设备的详细信息
- **认证**: 需要Token

**路径参数**:
- `device_id`: 设备ID

**响应示例**:
```json
{
    "id": 1,
    "device_id": "ESP32-001",
    "device_name": "站点1温度传感器",
    "description": "位于仓库A区",
    "is_active": true,
    "last_seen": "2024-12-02T15:25:00Z",
    "created_at": "2024-12-02T15:30:00Z",
    "updated_at": "2024-12-02T15:30:00Z"
}
```

**注意**: 响应中不包含 `secret_key`（安全考虑）

### 5.4 激活设备
- **接口**: `POST /api/v1/devices/{device_id}/activate`
- **描述**: 激活指定设备（允许设备上传数据）
- **认证**: 需要Token

**路径参数**:
- `device_id`: 设备ID

**响应示例**:
```json
{
    "status": "success",
    "message": "Device activated"
}
```

### 5.5 停用设备
- **接口**: `POST /api/v1/devices/{device_id}/deactivate`
- **描述**: 停用指定设备（禁止设备上传数据）
- **认证**: 需要Token

**路径参数**:
- `device_id`: 设备ID

**响应示例**:
```json
{
    "status": "success",
    "message": "Device deactivated"
}
```

## 📤 6. ESP32数据上传（设备端）

### 6.1 上传包裹数据
- **接口**: `POST /api/v1/upload`
- **描述**: ESP32设备上传包裹监控数据
- **认证**: 设备认证（HMAC-SHA256签名）

**请求头要求**:
- `X-Device-ID`: 设备唯一标识（如：ESP32-001）
- `X-Signature`: HMAC-SHA256签名
- `X-Timestamp`: Unix时间戳（秒）

**请求体**:
```json
{
    "package_id": 1001,                    // 必填，包裹ID（正整数）
    "max_temperature": 24.5,               // 必填，最高温度值（-50 ~ 100°C）
    "avg_humidity": 65.2,                  // 必填，平均湿度值（0 ~ 100%）
    "over_threshold_time": 3600,           // 必填，超阈值时间（秒）
    "timestamp": 1701504000                // 必填，Unix时间戳（秒）
}
```

**请求示例**:
```http
POST /api/v1/upload
X-Device-ID: ESP32-001
X-Signature: a1b2c3d4e5f6...
X-Timestamp: 1701504000
Content-Type: application/json

{
    "package_id": 1001,
    "max_temperature": 24.5,
    "avg_humidity": 65.2,
    "over_threshold_time": 3600,
    "timestamp": 1701504000
}
```

**响应示例**:
```json
{
    "status": "success",
    "message": "Data for package 1001 received",
    "record_id": 123
}
```

**错误响应**:
- `401 Unauthorized`: 设备ID无效、签名错误或时间戳超出范围
- `403 Forbidden`: 设备未激活
- `400 Bad Request`: 请求参数错误

**签名生成规则**:
1. 构建签名字符串：`package_id={package_id}&max_temperature={max_temperature}&avg_humidity={avg_humidity}&over_threshold_time={over_threshold_time}&timestamp={timestamp}`
2. 使用设备的 `secret_key` 对签名字符串进行 HMAC-SHA256 加密
3. 将结果转换为十六进制字符串

**注意事项**:
- 时间戳允许误差：±5分钟
- 设备必须先注册并激活
- 签名验证失败会拒绝请求

## ❌ 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

## 🔧 前端集成示例

### JavaScript/Axios示例

```javascript
// 设置基础URL和拦截器
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 10000
});

// 请求拦截器 - 添加Token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 响应拦截器 - 处理错误
api.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            // Token过期，跳转登录
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// 使用示例
// 登录
const login = async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    localStorage.setItem('token', response.data.token);
    return response;
};

// 获取包裹列表
const getPackages = async (page = 1, size = 10) => {
    return await api.get('/packages', { params: { page, size } });
};

// 获取包裹站点记录
const getPackageRecords = async (packageId, limit = 1000, offset = 0) => {
    return await api.get(`/packages/${packageId}/records`, { 
        params: { limit, offset } 
    });
};

// 绑定包裹
const bindPackage = async (packageId, packageName, description) => {
    return await api.post('/packages/bind', {
        package_id: packageId,
        package_name: packageName,
        description: description
    });
};
```

## 📝 注意事项

1. **Token过期**: JWT Token有效期为7天，过期后需要重新登录
2. **数据权限**: 用户只能访问自己绑定的包裹数据，未绑定的包裹会返回403错误
3. **分页查询**: 大数据量查询建议使用分页（limit/offset），避免一次性获取过多数据
4. **时间格式**: 所有时间字段使用ISO 8601格式（UTC时间），时间戳使用Unix时间戳（秒）
5. **包裹ID**: 包裹ID由ESP32设备决定，需要确保唯一性
6. **设备认证**: ESP32设备上传数据需要先注册设备并获取secret_key
7. **设备管理**: 设备需要先注册并激活才能上传数据
8. **包裹绑定**: 用户必须先绑定包裹才能查询包裹数据
9. **数据字段**: 每条记录包含：最大温度、平均湿度、超阈值时间、时间戳
10. **Secret Key安全**: 设备注册时返回的secret_key只显示一次，请妥善保管

## 🚀 在线API文档

启动服务器后，可以访问以下地址查看交互式API文档：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

这些页面提供了完整的接口测试功能，可以直接在浏览器中测试所有API接口。
