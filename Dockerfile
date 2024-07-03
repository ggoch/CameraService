FROM python:3.10.5-slim AS builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

# 工作目录
WORKDIR /usr/backend

# 安装构建依赖
RUN apt-get update && apt-get install -y gcc libpq-dev

# 复制 requirements.txt 并安装依赖
COPY ./requirements-image.txt /usr/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 创建最终镜像
FROM python:3.10.5-slim


# 创建非 root 用户
RUN useradd -ms /bin/bash celeryuser

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

# 工作目录
WORKDIR /usr/backend

# 安装运行时依赖
RUN apt-get update && apt-get install -y libpq5 libgl1-mesa-glx libglib2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制已安装的包
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . /usr/backend/