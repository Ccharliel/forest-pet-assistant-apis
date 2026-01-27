# 第1行：基础镜像选择
FROM python:3.10-slim

# 第2行：设置工作目录
WORKDIR /app

# 第3行：复制依赖文件
COPY requirements.txt .

# 第4行：安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 第5行：复制应用代码
COPY . .

# 第6行：启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]