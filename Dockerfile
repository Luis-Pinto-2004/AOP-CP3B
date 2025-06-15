# ---- Etapa 1: Builder com PyTorch + CUDA ----
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime AS builder

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código e pesos
COPY src/      ./src/
COPY .well-known/ ./.well-known/
COPY yolov8n.pt   ./

# ---- Etapa 2: Runtime mais leve ----
FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

# Dependências de SO
RUN apt-get update && apt-get install -y \
        python3-pip libgl1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia só o que precisamos do builder
COPY --from=builder /app /app

EXPOSE 8000
ENV PORT=8000

# Comando de arranque
CMD ["uvicorn", "api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--app-dir", "src"]
