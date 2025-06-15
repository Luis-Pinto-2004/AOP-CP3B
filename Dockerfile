# Dockerfile (única etapa – CPU-only)

FROM python:3.10-slim

WORKDIR /app

# 1) Instala dependências de SO para OpenCV
RUN apt-get update && \
    apt-get install -y \
      libgl1 \
      libglib2.0-0 \
      libsm6 \
      libxext6 \
      libxrender1 && \
    rm -rf /var/lib/apt/lists/*

# 2) Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copia a app, manifesto e pesos
COPY src/           ./src/
COPY .well-known/   ./.well-known/
COPY yolov8n.pt     ./

# 4) Expõe a porta do Uvicorn e arranca
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
