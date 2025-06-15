# Dockerfile

# 1) Base: Python 3.10 slim
FROM python:3.10-slim

WORKDIR /app

# 2) Dependências de SO (OpenCV headless)
RUN apt-get update && \
    apt-get install -y libgl1 && \
    rm -rf /var/lib/apt/lists/*

# 3) Copia requirements e instala tudo (inclui fastapi, uvicorn, ultralytics, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copia aplicação, manifesto e pesos
COPY src/           ./src/
COPY .well-known/   ./.well-known/
COPY yolov8n.pt     ./

EXPOSE 8000

# 5) Comando de arranque
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
