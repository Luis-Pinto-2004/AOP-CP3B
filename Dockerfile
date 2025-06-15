# ---- Etapa 1 (builder) ----
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime AS builder
WORKDIR /app

# Copia só o requirements e instala primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto da app
COPY src/       ./src/
COPY .well-known/ ./.well-known/
COPY yolov8n.pt   ./

# ---- Etapa 2 (runtime) ----
FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04
WORKDIR /app

# Dependências do sistema (ex: OpenCV)
RUN apt-get update && \
    apt-get install -y python3 python3-pip libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Copia tudo do builder
COPY --from=builder /app /app

EXPOSE 8000
CMD ["uvicorn", "api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--app-dir", "src"]
