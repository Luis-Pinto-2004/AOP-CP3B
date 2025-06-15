##############################################
# Uma só etapa: PyTorch + FastAPI + Uvicorn
##############################################
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

# 1) Dependências de SO (OpenCV, GTK, etc)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copia código, pesos e manifestos
COPY src/         ./src/
COPY .well-known/ ./.well-known/
COPY yolov8n.pt   ./

# 4) Expõe a porta e define o entrypoint
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
