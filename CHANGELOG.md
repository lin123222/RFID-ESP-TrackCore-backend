# 更新日志

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2024-11-26

### 新增
- ✨ 实现分层架构（路由层、业务层、数据访问层、模型层）
- ✨ 包裹数据上传接口 `/api/v1/upload`
- ✨ 包裹历史查询接口 `/api/v1/packages/{id}/records`
- ✨ 获取最新记录接口 `/api/v1/packages/{id}/latest`
- ✨ 健康检查接口 `/api/v1/health`
- ✨ 温度异常自动检测和告警
- ✨ 基于 Pydantic 的数据验证
- ✨ SQLAlchemy ORM 数据库操作
- ✨ Alembic 数据库迁移支持
- ✨ Loguru 结构化日志系统
- ✨ 自动生成 API 文档（Swagger/ReDoc）
- ✨ 完整的单元测试和集成测试
- ✨ 数据库初始化脚本
- ✨ 测试数据填充脚本

### 技术栈
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- MySQL 8.0+
- Python 3.9+

### 数据库
- `package_records` 表：存储包裹温度记录
- 索引优化：package_id, timestamp, 复合索引

### 文档
- README.md - 项目说明和快速开始
- DEPLOYMENT.md - 部署指南
- API_EXAMPLES.md - API 使用示例
- CHANGELOG.md - 更新日志

## [未来计划]

### v1.1.0
- [ ] 添加用户认证和授权
- [ ] 实现数据导出功能（CSV/Excel）
- [ ] 添加实时数据推送（WebSocket）
- [ ] 性能优化和缓存机制

### v1.2.0
- [ ] 添加数据可视化仪表板
- [ ] 邮件/短信告警通知
- [ ] 批量数据上传支持
- [ ] 数据统计和分析功能

### v2.0.0
- [ ] 微服务架构重构
- [ ] 支持多种数据库（PostgreSQL, MongoDB）
- [ ] 容器化部署优化
- [ ] 国际化支持
