########################################
# STAGE 1: instala tudo (builder)     #
########################################
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/         ./src/
COPY .well-known/ ./.well-known/
COPY yolov8n.pt   ./

########################################
# STAGE 2: runtime mais leve (CPU-only)#
########################################
FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Copia tanto o código como as libs instaladas no builder:
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app                /app

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
