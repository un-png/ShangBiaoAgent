#!/bin/bash
set -e

# 如果挂载了.env则使用，否则用镜像内置的
if [ -f /app/data/.env ]; then
    cp /app/data/.env /app/.env
    echo "[entry] 使用挂载的 .env 配置"
fi

# 确保数据库在持久化目录
if [ ! -f /app/data/trademarks.db ] && [ -f /app/trademarks.db ]; then
    cp /app/trademarks.db /app/data/trademarks.db
fi
ln -sf /app/data/trademarks.db /app/trademarks.db

echo "[entry] 启动邮件提醒Worker..."
python -B reminder_worker.py &
WORKER_PID=$!

echo "[entry] 启动Streamlit Web服务 (端口8501)..."
streamlit run main.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &
WEB_PID=$!

# 任意进程退出则全部退出
wait -n $WORKER_PID $WEB_PID
