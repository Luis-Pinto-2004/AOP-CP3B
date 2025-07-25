# src/api/main.py

import io
import os
import cv2
import numpy as np
import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from inference import detect
from utils.draw import draw_boxes

# 1. Instancia a app
app = FastAPI(
    title="MCP Server – Gato vs Cão",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs"
)

# 2. Monta a pasta .well-known para servir manifestos e logo
app.mount(
    "/.well-known",
    StaticFiles(directory=".well-known", html=False),
    name="well-known"
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


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
    usando skip + redução de resolução e grava o resultado em output_path.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Não foi possível abrir vídeo {input_path}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps    = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # parâmetros de performance
    skip = 2                # processar 1 em cada 2 frames
    target_w = 640          # largura para inferência
    target_h = int(height * target_w / width)

    cached_detections = []
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # só faz inferência a cada 'skip' frames
        if frame_id % skip == 0:
            # redimensiona para acelerar
            small = cv2.resize(frame, (target_w, target_h))
            dets_small = detect(small)
            # escala detecções de volta ao tamanho original
            scaled = []
            sx = width / target_w
            sy = height / target_h
            for d in dets_small:
                x1, y1, x2, y2 = d['box']
                scaled.append({
                    'box': [
                        int(x1 * sx), int(y1 * sy),
                        int(x2 * sx), int(y2 * sy)
                    ],
                    'label': d['label'],
                    'conf': d['conf']
                })
            cached_detections = scaled

        # desenha caixas (mesmo nos frames em que não inferimos)
        annotated = draw_boxes(frame, cached_detections)
        out.write(annotated)
        frame_id += 1

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
