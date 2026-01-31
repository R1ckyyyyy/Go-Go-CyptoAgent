FROM python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码 (注意：构建上下文应该是 backend 目录)
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令 (使用 uvicorn 运行 main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
