# RFID包裹监控系统 API接口文档

## 📋 基础信息

- **服务器地址**: `http://localhost:8000`
- **API版本**: `v1`
- **基础路径**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 🔐 认证说明

除了健康检查和用户注册/登录接口外，所有接口都需要在请求头中携带JWT Token：

```http
Authorization: Bearer {your_jwt_token}
```

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
    "password": "password123",       // 必填，密码，6-50字符
    "nickname": "用户昵称"           // 可选，昵称
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
        "nickname": "用户昵称",
        "status": 1,
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
        "nickname": "用户昵称",
        "status": 1,
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
    "email": "newemail@example.com",  // 可选，新邮箱
    "nickname": "新昵称"              // 可选，新昵称
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

## 📊 4. 数据监控

### 4.1 获取包裹监控详情
- **接口**: `GET /api/v1/monitor/{package_id}`
- **描述**: 获取包裹的监控详情和统计信息
- **认证**: 需要Token

**路径参数**:
- `package_id`: 包裹ID

**响应示例**:
```json
{
    "status": "success",
    "message": "获取成功",
    "data": {
        "package_id": 1001,
        "package_name": "重要文件包裹",
        "description": "包含重要合同文件",
        "current_data": {
            "temperature": 24.5,
            "humidity": 65.2,
            "timestamp": "2024-12-02T15:25:00Z"
        },
        "statistics": {
            "total_records": 150,
            "avg_temperature": 23.8,
            "avg_humidity": 62.5,
            "date_range": {
                "start": "2024-11-25T00:00:00Z",
                "end": "2024-12-02T15:25:00Z"
            }
        }
    }
}
```

### 4.2 获取包裹历史记录
- **接口**: `GET /api/v1/monitor/{package_id}/records`
- **描述**: 获取包裹的历史监控记录
- **认证**: 需要Token

**路径参数**:
- `package_id`: 包裹ID

**查询参数**:
- `page`: 页码，默认1
- `size`: 每页数量，默认100，最大1000
- `start_date`: 开始日期，格式：2024-12-01T00:00:00Z（可选）
- `end_date`: 结束日期，格式：2024-12-02T23:59:59Z（可选）

**请求示例**:
```
GET /api/v1/monitor/1001/records?page=1&size=100&start_date=2024-12-01T00:00:00Z
```

**响应示例**:
```json
{
    "status": "success",
    "message": "获取成功",
    "data": {
        "total": 150,
        "page": 1,
        "size": 100,
        "records": [
            {
                "id": 1,
                "max_temperature": 24.5,
                "avg_humidity": 65.2,
                "over_threshold_time": 0,
                "timestamp": 1701504000,
                "created_at": "2024-12-02T15:25:00Z"
            }
        ]
    }
}
```

### 4.3 获取包裹统计分析
- **接口**: `GET /api/v1/monitor/{package_id}/statistics`
- **描述**: 获取包裹的详细统计分析
- **认证**: 需要Token

**路径参数**:
- `package_id`: 包裹ID

**查询参数**:
- `period`: 统计周期，可选值：1d, 7d, 30d，默认7d

**请求示例**:
```
GET /api/v1/monitor/1001/statistics?period=7d
```

**响应示例**:
```json
{
    "status": "success",
    "message": "获取成功",
    "data": {
        "period": "7d",
        "total_records": 150,
        "temperature": {
            "avg": 23.8,
            "min": 18.2,
            "max": 28.5
        },
        "humidity": {
            "avg": 62.5,
            "min": 45.0,
            "max": 78.0
        },
        "daily_stats": [
            {
                "date": "2024-12-02",
                "avg_temp": 24.2,
                "avg_humidity": 63.1,
                "record_count": 24
            },
            {
                "date": "2024-12-01",
                "avg_temp": 23.5,
                "avg_humidity": 61.8,
                "record_count": 24
            }
        ]
    }
}
```

### 4.4 导出包裹数据
- **接口**: `GET /api/v1/monitor/{package_id}/export`
- **描述**: 导出包裹的所有监控数据
- **认证**: 需要Token

**路径参数**:
- `package_id`: 包裹ID

**查询参数**:
- `format`: 导出格式，目前只支持csv

**请求示例**:
```
GET /api/v1/monitor/1001/export?format=csv
```

**响应**: 直接返回CSV文件下载

## 📤 5. ESP32数据上传（设备端）

### 5.1 上传包裹数据
- **接口**: `POST /api/v1/upload`
- **描述**: ESP32设备上传包裹监控数据
- **认证**: 无需认证

**请求参数**:
```json
{
    "package_id": 1001,           // 必填，包裹ID
    "temperature": 24.5,          // 必填，温度值
    "timestamp": 1701504000       // 必填，Unix时间戳
}
```

**响应示例**:
```json
{
    "status": "success",
    "message": "数据上传成功",
    "data": {
        "id": 1,
        "package_id": 1001,
        "max_temperature": 24.5,
        "avg_humidity": 65.2,
        "over_threshold_time": 0,
        "timestamp": 1701504000,
        "created_at": "2024-12-02T15:25:00Z"
    }
}
```

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

// 获取包裹历史数据
const getPackageRecords = async (packageId, page = 1, size = 100) => {
    return await api.get(`/monitor/${packageId}/records`, { 
        params: { page, size } 
    });
};
```

## 📝 注意事项

1. **Token过期**: JWT Token有效期为7天，过期后需要重新登录
2. **数据权限**: 用户只能访问自己绑定的包裹数据
3. **分页查询**: 大数据量查询建议使用分页，避免一次性获取过多数据
4. **时间格式**: 所有时间字段使用ISO 8601格式（UTC时间）
5. **包裹ID**: 包裹ID由ESP32设备决定，需要确保唯一性

## 🚀 在线API文档

启动服务器后，可以访问以下地址查看交互式API文档：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

这些页面提供了完整的接口测试功能，可以直接在浏览器中测试所有API接口。
