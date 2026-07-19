FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制源码
COPY main.py .
COPY services/ ./services/

# 复制启动脚本
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 暴露Streamlit端口
EXPOSE 8501

# 数据库和.env通过volume挂载，不打包进镜像
VOLUME ["/app/data"]

ENTRYPOINT ["./entrypoint.sh"]
