# RFID 物流包裹温控数据采集系统 - 后端

基于 FastAPI 的分层架构后端服务，支持用户管理、包裹监控和数据分析的完整Web应用后端。

## 📋 项目特性

- ✅ **分层架构**：路由层、业务层、数据访问层、模型层清晰分离
- ✅ **用户系统**：JWT认证、用户注册登录、权限控制
- ✅ **包裹管理**：用户包裹绑定、多用户数据隔离
- ✅ **数据监控**：历史数据查询、统计分析、数据导出
- ✅ **类型安全**：使用 Pydantic 进行数据验证
- ✅ **数据库支持**：MySQL + SQLAlchemy ORM
- ✅ **API 文档**：自动生成 Swagger/ReDoc 文档
- ✅ **日志系统**：基于 Loguru 的结构化日志
- ✅ **安全认证**：JWT Token + 密码加密存储

## 🏗️ 项目结构

```
network_backend/
├── app/
│   ├── api/              # 路由层
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   ├── core/             # 核心配置
│   │   ├── config.py
│   │   └── database.py
│   ├── models/           # 数据模型
│   ├── schemas/          # 数据验证
│   ├── services/         # 业务逻辑
│   ├── repositories/     # 数据访问
│   └── utils/            # 工具函数
├── scripts/              # 工具脚本
├── tests/                # 测试
└── requirements.txt
```

## 🚀 快速开始

### 1. 环境准备

**系统要求**：
- Python 3.9+
- MySQL 5.7+ / 8.0+

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库连接
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=your_password
# MYSQL_DATABASE=rfid_system
```

### 4. 初始化数据库

```bash
# 创建数据库（在 MySQL 中执行）
CREATE DATABASE rfid_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 运行初始化脚本
python scripts/init_db.py

# （可选）填充测试数据
python scripts/seed_data.py
```

### 5. 启动服务

```bash
# 方式1：使用一键启动脚本（推荐）
python scripts/setup_and_run.py

# 方式2：手动启动
# 先创建用户表
python scripts/create_user_tables.py
# 再启动服务
python run.py

# 方式3：使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问 API 文档

启动后访问：
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 📡 API 接口

### 1. 健康检查

```http
GET /api/v1/health
```

### 2. 用户认证

```http
# 用户注册
POST /api/v1/auth/register
# 用户登录
POST /api/v1/auth/login
# 获取用户信息
GET /api/v1/auth/me
```

### 3. 包裹管理

```http
# 绑定包裹
POST /api/v1/packages/bind
# 获取包裹列表
GET /api/v1/packages
# 获取包裹详情
GET /api/v1/packages/{package_id}
```

### 4. 数据监控

```http
# 获取包裹历史记录
GET /api/v1/monitor/{package_id}/records
# 获取统计分析
GET /api/v1/monitor/{package_id}/statistics
# 导出数据
GET /api/v1/monitor/{package_id}/export
```

### 5. ESP32 数据上传

```http
POST /api/v1/upload
Content-Type: application/json

{
  "package_id": 1001,
  "temperature": 24.5,
  "timestamp": 1700000000
}
```

## 🗄️ 数据库表结构

### `users` 表 - 用户信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 用户名，唯一 |
| email | VARCHAR(100) | 邮箱 |
| password_hash | VARCHAR(255) | 密码哈希 |
| nickname | VARCHAR(100) | 昵称 |
| status | INT | 状态：1正常 0禁用 |
| is_active | BOOLEAN | 是否激活 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### `user_packages` 表 - 用户包裹关联

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 用户ID |
| package_id | INT | 包裹ID |
| package_name | VARCHAR(100) | 包裹名称 |
| description | VARCHAR(500) | 包裹描述 |
| is_active | BOOLEAN | 是否激活 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### `package_records` 表 - 包裹监控记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| package_id | INT | 包裹ID |
| max_temperature | FLOAT | 最高温度(°C) |
| avg_humidity | FLOAT | 平均湿度(%) |
| over_threshold_time | INT | 超阈值时间(秒) |
| timestamp | BIGINT | Unix时间戳 |
| created_at | DATETIME | 记录创建时间 |

## 🔧 配置说明

### 温度阈值

在 `.env` 文件中配置：

```env
TEMP_HIGH_THRESHOLD=30.0   # 高温阈值
TEMP_LOW_THRESHOLD=-10.0   # 低温阈值
```

当温度超出阈值时，系统会自动记录警告日志。

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api/test_package.py

# 查看测试覆盖率
pytest --cov=app tests/
```

## 📝 开发指南

### 添加新功能

1. **添加数据模型**：在 `app/models/` 中定义
2. **添加数据验证**：在 `app/schemas/` 中定义
3. **添加数据访问**：在 `app/repositories/` 中实现
4. **添加业务逻辑**：在 `app/services/` 中实现
5. **添加 API 端点**：在 `app/api/v1/endpoints/` 中实现

### 代码规范

- 使用类型注解
- 遵循 PEP 8 规范
- 编写文档字符串
- 添加单元测试

## 🐛 常见问题

### 1. 数据库连接失败

检查：
- MySQL 服务是否启动
- `.env` 中的数据库配置是否正确
- 数据库是否已创建

### 2. 端口被占用

修改 `.env` 中的 `SERVER_PORT` 配置

### 3. 依赖安装失败

尝试升级 pip：
```bash
pip install --upgrade pip
```

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！
