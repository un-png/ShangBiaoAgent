#!/bin/bash
set -e

echo "[entry] === 商标AI智能助手 容器启动 ==="

# 挂载 data/ 目录
mkdir -p /app/data

# 从挂载的 .env 导出环境变量（最可靠的方式）
if [ -f /app/data/.env ]; then
    echo "[entry] 从 /app/data/.env 加载环境变量"
    set -a
    source /app/data/.env
    set +a
    # 同时复制一份供 Python dotenv 读取
    cp /app/data/.env /app/.env
else
    echo "[entry] ⚠️  未找到 /app/data/.env, 请挂载配置文件!"
fi

# 数据库软链接到持久化目录
if [ -f /app/data/trademarks.db ]; then
    ln -sf /app/data/trademarks.db /app/trademarks.db
else
    touch /app/data/trademarks.db
    ln -sf /app/data/trademarks.db /app/trademarks.db
fi

echo "[entry] 启动邮件提醒Worker..."
python -B reminder_worker.py &
WORKER_PID=$!

echo "[entry] 启动Streamlit Web服务 (端口8501)..."
streamlit run main.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &
WEB_PID=$!

echo "[entry] 所有服务已启动"
echo "[entry] Web: http://0.0.0.0:8501"
echo "[entry] Worker PID: $WORKER_PID | Web PID: $WEB_PID"

wait -n $WORKER_PID $WEB_PID
