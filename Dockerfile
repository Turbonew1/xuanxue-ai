FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir -e "." && \
    pip install --no-cache-dir fastapi "uvicorn[standard]"

EXPOSE 8600

CMD ["python", "-m", "xuanxue.server"]
