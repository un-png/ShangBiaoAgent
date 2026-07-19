#!/bin/bash
# 商标AI智能助手 - Linux Docker 一键部署脚本
set -e

echo "========================================"
echo "  商标AI智能助手 - Docker 部署"
echo "========================================"

# ---------- 1. 检查 Docker ----------
if ! command -v docker &>/dev/null; then
    echo ""
    echo ">>> 第0步：安装 Docker <<<"
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
    echo "Docker 安装完成"
fi

if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null; then
    echo "安装 docker-compose..."
    apt-get update && apt-get install -y docker-compose-plugin
fi

echo ""
echo ">>> Docker 环境检查通过 <<<"
docker --version

# ---------- 2. 准备数据目录 ----------
echo ""
echo ">>> 第1步：准备持久化目录 <<<"
mkdir -p data

# 如果没有 .env 文件在 data/ 下，提示用户
if [ ! -f data/.env ]; then
    echo ""
    echo "⚠️  未找到 data/.env 配置文件！"
    echo ""
    echo "请先创建 data/.env 文件，内容参考："
    echo "-----------------------------------------"
    cat <<'TEMPLATE'
DASHSCOPE_API_KEY="你的阿里云DashScope API Key"
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
TRADEMARK_APPCODE="你的阿里云商标API AppCode"

SMTP_HOST="smtp.qq.com"
SMTP_PORT=587
SMTP_USER="你的QQ邮箱@qq.com"
SMTP_PASSWORD="你的QQ邮箱授权码"
SMTP_FROM="你的QQ邮箱@qq.com"
TEMPLATE
    echo "-----------------------------------------"
    echo ""
    read -p "按回车键继续（记得配置好 data/.env 后再启动）..."
fi

# ---------- 3. 构建&启动 ----------
echo ""
echo ">>> 第2步：构建镜像并启动 <<<"
docker compose up -d --build

echo ""
echo ">>> 第3步：等待服务启动 <<<"
sleep 5

# ---------- 4. 检查状态 ----------
echo ""
echo ">>> 第4步：检查运行状态 <<<"
docker compose ps
docker compose logs --tail=20

# ---------- 5. 完成 ----------
echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "  访问地址: http://$(hostname -I 2>/dev/null | awk '{print $1}' || echo '服务器IP'):8501"
echo ""
echo "  常用命令:"
echo "    查看日志:  docker compose logs -f"
echo "    重启服务:  docker compose restart"
echo "    停止服务:  docker compose down"
echo "    更新代码:  docker compose up -d --build"
echo ""
