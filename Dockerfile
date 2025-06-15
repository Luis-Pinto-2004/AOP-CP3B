# ---- Etapa 1: Construção ----
FROM pytorch/pytorch:2.0-cuda11.7-cudnn8-runtime AS builder

WORKDIR /app

# Copia ficheiros de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código fonte
COPY src/ ./src/
COPY .well-known/ ./.well-known/
COPY yolov8n.pt ./

# ---- Etapa 2: Runtime mais leve ----
FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

# Instala Python e dependências mínimas
RUN apt-get update && apt-get install -y \
    python3 python3-pip libgl1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia do builder
COPY --from=builder /app /app

# Expõe a porta usada pelo Uvicorn
EXPOSE 8000

# Variável PORT para compatibilidade com plataformas cloud
ENV PORT=8000

# Comando para arrancar o servidor
CMD ["uvicorn", "api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--app-dir", "src", \
     "--reload"]
