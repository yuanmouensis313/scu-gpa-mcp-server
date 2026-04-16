# 多阶段构建四川大学绩点MCP服务器
FROM python:3.12-slim-bookworm as base

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml requirements.txt ./
COPY server.py ./

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8081

# 暴露端口（Smithery平台标准端口）
EXPOSE 8081

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 运行MCP服务器
CMD ["python", "server.py"]