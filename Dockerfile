##############################################
# == STAGE 1: Builder (com PyTorch pré-instalado) ==
##############################################
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime AS builder
WORKDIR /app

# 1) copia apenas o requirements corrigido
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) copia o código-fonte, o manifesto e o logo, e os pesos
COPY src/           ./src/
COPY .well-known/   ./.well-known/
COPY yolov8n.pt     ./

##############################################
# == STAGE 2: Runtime mais leve ==
##############################################
FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04
WORKDIR /app

# instala dependências de SO (OpenCV headless)
RUN apt-get update && \
    apt-get install -y python3 python3-pip libgl1 && \
    rm -rf /var/lib/apt/lists/*

# traz tudo do builder
COPY --from=builder /app /app

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
