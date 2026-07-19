# 商标AI智能助手

AI驱动的一站式商标服务平台：智能起名 → Logo设计 → 品牌故事 → 商标查询 → 风险评估 → 到期提醒。

## 功能一览

| 功能 | 说明 |
|------|------|
| 一站式起名 | 描述业务需求，AI自动生成商标名称、Logo、品牌故事 |
| 商标查询 | 对接国家商标网API，实时查询商标注册情况 |
| 风险评估 | AI分析近似商标，给出注册成功率评分和策略建议 |
| 智能问答 | 自然语言输入，自动解析意图并返回分析结果 |
| 到期提醒 | 绑定商标后，到期自动发送邮件提醒 |

## 技术栈

| 组件 | 选型 |
|------|------|
| 前端 | Streamlit |
| AI框架 | LangChain + ChatOpenAI |
| 大模型 | 通义千问 Qwen-Plus（DashScope） |
| 文生图 | Qwen-Image / 通义万相 |
| 商标数据 | 阿里云商标搜索API + SQLite本地库 |
| 邮件发送 | SMTP |
| 部署 | Docker + Docker Compose |

---

## 一、本地部署（Windows）

### 1. 环境要求

- Python 3.10+
- Git

### 2. 克隆项目

```bash
git clone git@github.com:un-png/shangbiao_agent.git
cd shangbiao_agent
```

### 3. 创建虚拟环境

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置环境变量

```bash
copy .env.example .env
notepad .env
```

填入你的真实配置：

```ini
# -------- 阿里云 DashScope（大模型+文生图）--------
# 获取地址：https://dashscope.console.aliyun.com/
DASHSCOPE_API_KEY="sk-xxx"
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# -------- 阿里云商标搜索API（可选，不配则用本地模拟数据）--------
# 获取地址：https://market.aliyun.com/products/57002002/cmapi00046967.html
TRADEMARK_APPCODE="你的AppCode"

# -------- 邮件发送（可选，不配则不发邮件）--------
# QQ邮箱授权码获取：QQ邮箱 → 设置 → 账户 → POP3/SMTP服务 → 生成授权码
SMTP_HOST="smtp.qq.com"
SMTP_PORT=587
SMTP_USER="your_email@qq.com"
SMTP_PASSWORD="你的QQ邮箱授权码"
SMTP_FROM="your_email@qq.com"
```

### 6. 启动Web服务

```bash
streamlit run main.py
```

浏览器访问 `http://localhost:8501`

### 7. （可选）启动邮件提醒定时任务

另开一个终端：

```bash
.venv\Scripts\activate
python -B reminder_worker.py
```

每10分钟自动扫描到期商标，发送邮件提醒。

---

## 二、Linux Docker 部署

### 1. 环境要求

- Linux 服务器（CentOS 7+/Ubuntu 20.04+/Debian 11+）
- Docker + Docker Compose

### 2. 安装 Docker

```bash
# 一键安装
curl -fsSL https://get.docker.com | bash

# 启动并设置开机自启
systemctl enable docker
systemctl start docker

# 验证
docker --version
```

### 3. 配置 Docker 镜像加速（国内必做）

```bash
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.1ms.run"
  ]
}
EOF

systemctl daemon-reload
systemctl restart docker
```

### 4. 克隆项目

```bash
cd /opt
git clone git@github.com:un-png/shangbiao_agent.git
cd shangbiao_agent
```

### 5. 配置环境变量

```bash
cp .env.example data/.env
vi data/.env
```

填入真实配置（同上方 .env 内容）。

### 6. 构建并启动

```bash
docker compose up -d --build
```

### 7. 验证

```bash
# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f
```

浏览器访问 `http://服务器IP:8501`

### 8. 配置 Nginx 反向代理（可选）

```bash
# 安装 Nginx
apt-get install -y nginx

# 创建站点配置
vi /etc/nginx/sites-available/shangbiao
```

```nginx
server {
    listen 80;
    server_name trademark.你的域名.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
        client_max_body_size 50m;
    }
}
```

```bash
# 启用站点
ln -s /etc/nginx/sites-available/shangbiao /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 申请免费HTTPS证书
certbot --nginx -d trademark.你的域名.com
```

### 9. 开放防火墙端口

```bash
# 云服务器安全组中放行 8501 端口

# CentOS 系统防火墙
firewall-cmd --add-port=8501/tcp --permanent && firewall-cmd --reload

# Ubuntu 系统防火墙
ufw allow 8501
```

---

## 三、常用运维命令

### Docker 管理

```bash
docker compose ps              # 查看容器状态
docker compose logs -f         # 实时查看日志
docker compose restart         # 重启服务
docker compose down            # 停止并删除容器
docker compose up -d           # 启动（不重建镜像）
docker compose up -d --build   # 重新构建镜像并启动
docker compose exec shangbiao bash  # 进入容器调试
```

### 更新代码

```bash
git pull
docker compose down
docker compose up -d --build
```

数据库文件在 `data/trademarks.db`，不会因重建镜像丢失。

### 查看邮件提醒日志

```bash
docker compose logs -f | grep Mail
```

---

## 四、目录结构

```
shangbiao_agent/
├── main.py                  # Streamlit Web 主程序
├── reminder_worker.py       # 邮件提醒定时任务
├── entrypoint.sh            # Docker 容器启动脚本
├── Dockerfile               # Docker 镜像构建文件
├── docker-compose.yml       # Docker 编排文件
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
├── deploy.sh                # Linux 一键部署脚本
├── data/                    # 持久化目录（.env + 数据库）
│   └── .gitkeep
└── services/                # 服务层模块
    ├── config.py            # 配置与常量
    ├── llm_service.py       # LangChain LLM 服务
    ├── logo_service.py      # Qwen 文生图
    ├── database.py          # SQLite 数据库
    ├── trademark_api.py     # 阿里云商标搜索API
    ├── trademark_tool.py    # LangChain 工具封装
    └── mail_service.py      # SMTP 邮件发送
```

---

## 五、常见问题

**Q: 商标查询返回空？**

A: 检查 `.env` 中 `TRADEMARK_APPCODE` 是否配置正确。未配置时页面左上角显示"模拟数据模式"，仅使用本地演示数据。

**Q: Logo 生成失败？**

A: 确保 `DASHSCOPE_API_KEY` 有效且有余额。文生图需要在 DashScope 开通通义万相服务。

**Q: 不配 SMTP 能用吗？**

A: 可以，除了邮件发送功能外，其他功能不受影响。定时任务会运行但跳过发邮件。

**Q: 怎么更换大模型？**

A: 编辑 `services/llm_service.py`，修改 `model="qwen-plus"` 为其他模型如 `qwen-max`、`qwen-turbo`。

**Q: 容器启动报错？**

A: 先检查 `data/.env` 是否存在：`ls -la data/.env`，确保路径正确且内容完整。
