# src/inference.py
import numpy as np
from ultralytics import YOLO

# Carregue o modelo só uma vez
_model = YOLO('yolov8n.pt')  # use fine-tuned weights quando disponíveis

def detect(frame: np.ndarray):
    """
    Recebe frame BGR, devolve lista de deteções:
    [{ 'box': [x1,y1,x2,y2], 'label': str, 'conf': float }, …]
    """
    results = _model(frame)[0]
    detections = []
    for *box, conf, cls in results.boxes.data.tolist():
        if int(cls) in (15, 16):  # 15=gato, 16=cão no COCO
            label = 'gato' if int(cls)==15 else 'cão'
            detections.append({
                'box': box,
                'label': label,
                'conf': float(conf)
            })
    return detections
