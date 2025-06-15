# src/api/main.py
import io, cv2, numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from inference import detect
from utils.draw import draw_boxes

app = FastAPI(title="MCP Server – Gato vs Cão")

@app.post("/detect-image")
async def detect_image(file: UploadFile = File(...)):
    data = await file.read()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(400, "Ficheiro inválido")
    detections = detect(frame)
    annotated = draw_boxes(frame, detections)
    _, buf = cv2.imencode('.jpg', annotated)
    return StreamingResponse(io.BytesIO(buf.tobytes()),
                             media_type="image/jpeg")

# Em seguida, crie endpoint /detect-video com lógica semelhante, iterando frames.
