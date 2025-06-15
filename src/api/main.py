# src/api/main.py

import io
import os
import cv2
import numpy as np
import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from inference import detect
from utils.draw import draw_boxes

# 1. Instancia a app
app = FastAPI(title="MCP Server – Gato vs Cão", version="0.1.0")

# 2. Monta a pasta .well-known para servir manifestos e logo
app.mount(
    "/.well-known",
    StaticFiles(directory=".well-known", html=False),
    name="well-known"
)

@app.post("/detect-image", summary="Detetar e anotar imagem")
async def detect_image(file: UploadFile = File(...)):
    """
    Recebe uma imagem (JPEG/PNG), infere deteções de gato vs cão
    e devolve a mesma imagem com bounding-boxes e probabilidades.
    """
    data = await file.read()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Ficheiro inválido")

    detections = detect(frame)
    annotated = draw_boxes(frame, detections)
    success, buf = cv2.imencode('.jpg', annotated)
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao codificar imagem")

    return StreamingResponse(io.BytesIO(buf.tobytes()), media_type="image/jpeg")


def process_video(input_path: str, output_path: str):
    """
    Lê um vídeo de input_path, anota frame-a-frame
    e grava o resultado em output_path.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Não foi possível abrir vídeo {input_path}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps    = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detections = detect(frame)
        annotated  = draw_boxes(frame, detections)
        out.write(annotated)

    cap.release()
    out.release()


@app.post("/detect-video", summary="Detetar e anotar vídeo")
async def detect_video(file: UploadFile = File(...)):
    """
    Recebe um ficheiro de vídeo (MP4, AVI, ...), processa-o frame-a-frame
    e devolve o vídeo anotado.
    """
    # 1) Preparar paths temporários
    suffix = os.path.splitext(file.filename)[1] or ".mp4"
    input_fd,  input_path  = tempfile.mkstemp(suffix=suffix)
    output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
    os.close(input_fd);  os.close(output_fd)

    # 2) Gravar upload no disco
    content = await file.read()
    with open(input_path, "wb") as f:
        f.write(content)

    # 3) Processar vídeo de forma síncrona
    try:
        process_video(input_path, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4) Devolver ficheiro anotado apenas depois do processamento
    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=f"annotated_{file.filename}"
    )
