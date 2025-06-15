##############################################
# == STAGE 1: Builder (com PyTorch pré-instalado) ==
##############################################
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime AS builder
WORKDIR /app

# 1) só requirements.txt (remove torch/torchvision porque já vêm na imagem base)
COPY requirements.txt .
RUN sed -i '/^torch\\|^torchvision/d' requirements.txt \
 && pip install --no-cache-dir -r requirements.txt

# 2) copia o resto do código + pesos
COPY src/        ./src/
COPY .well-known/ ./.well-known/
COPY yolov8n.pt   ./

##############################################
# == STAGE 2: Runtime (usa a mesma base PyTorch) ==
##############################################
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime
WORKDIR /app

# Instala só as libs de SO que o OpenCV e GTK precisam
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 && \
    rm -rf /var/lib/apt/lists/*

# Traz tudo que o builder preparou (inclui torch, fastapi, uvicorn, etc)
COPY --from=builder /app /app

# Porta exposta (o uvicorn usará essa)
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
