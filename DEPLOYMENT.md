# 部署指南

## 🚀 生产环境部署

### 1. 服务器准备

**推荐配置**：
- CPU: 2核+
- 内存: 4GB+
- 系统: Ubuntu 20.04+ / CentOS 7+
- Python: 3.9+
- MySQL: 8.0+

### 2. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install python3.9 python3.9-venv python3-pip -y

# 安装 MySQL
sudo apt install mysql-server -y
```

### 3. 配置 MySQL

```bash
# 登录 MySQL
sudo mysql -u root -p

# 创建数据库和用户
CREATE DATABASE rfid_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rfid_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON rfid_system.* TO 'rfid_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. 部署应用

```bash
# 克隆代码
cd /opt
git clone <your-repo-url> network_backend
cd network_backend

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置
```

### 5. 初始化数据库

```bash
# 运行迁移
alembic upgrade head

# 或使用初始化脚本
python scripts/init_db.py
```

### 6. 使用 Systemd 管理服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/rfid-backend.service
```

内容：

```ini
[Unit]
Description=RFID Backend API Service
After=network.target mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/network_backend
Environment="PATH=/opt/network_backend/venv/bin"
ExecStart=/opt/network_backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable rfid-backend
sudo systemctl start rfid-backend
sudo systemctl status rfid-backend
```

### 7. 使用 Nginx 反向代理

安装 Nginx：

```bash
sudo apt install nginx -y
```

配置文件 `/etc/nginx/sites-available/rfid-backend`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/rfid-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. 配置 HTTPS（可选）

使用 Let's Encrypt：

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## 🐳 Docker 部署

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "run.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: rfid_system
      MYSQL_USER: rfid_user
      MYSQL_PASSWORD: rfid_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  backend:
    build: .
    depends_on:
      - mysql
    environment:
      MYSQL_HOST: mysql
      MYSQL_PORT: 3306
      MYSQL_USER: rfid_user
      MYSQL_PASSWORD: rfid_password
      MYSQL_DATABASE: rfid_system
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs

volumes:
  mysql_data:
```

启动：

```bash
docker-compose up -d
```

## 📊 监控和日志

### 查看日志

```bash
# 应用日志
tail -f logs/app_*.log

# Systemd 日志
sudo journalctl -u rfid-backend -f
```

### 性能监控

推荐工具：
- Prometheus + Grafana
- New Relic
- DataDog

## 🔒 安全建议

1. **使用强密码**：数据库和应用密码
2. **配置防火墙**：只开放必要端口
3. **定期更新**：系统和依赖包
4. **备份数据**：定期备份数据库
5. **限制 CORS**：生产环境设置具体域名
6. **使用 HTTPS**：加密传输

## 🔄 更新部署

```bash
cd /opt/network_backend
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart rfid-backend
```
