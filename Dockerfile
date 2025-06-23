# 使用支持 audioop 的 Python 版本
FROM python:3.11-slim

# 安装 ffmpeg（用于 pydub 处理 ogg）
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# 监听 Cloud Run 默认端口
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "bot:app"]
