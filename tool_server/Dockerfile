# 基础镜像选择
FROM python:3.10-slim
LABEL authors="Charlie"

# 设置工作目录
WORKDIR /app

# 更换 apt 为阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装 Git 和 各类依赖（避免报错）
RUN apt-get update && apt-get install -y \
    git \
    python3-tk \
    tk \
    ca-certificates \
    wget \
    curl \
    unzip \
    xdg-utils \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libnspr4 \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    libxshmfence1 \
    libxss1 \
    libxtst6 \
    libu2f-udev \
 && rm -rf /var/lib/apt/lists/*

# 复制 requirements.in
COPY requirements.in .

# 安装 pip-tools 用于编译依赖
RUN pip install --no-cache-dir pip-tools -i https://mirrors.aliyun.com/pypi/simple/

# 编译生成 requirements.txt
RUN pip-compile requirements.in -i https://mirrors.aliyun.com/pypi/simple/

# 装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
