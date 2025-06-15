import numpy as np
import torch
from ultralytics import YOLO
import ultralytics.nn.tasks

# Permitir o carregamento seguro da classe DetectionModel
torch.serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])

# Carregue o modelo apenas uma vez, usando o YOLO da Ultralytics
def _load_model():
    """
    Função auxiliar para carregar o modelo, garantindo que as dependências
    de deserialização são permitidas.
    """
    # No caso de precisar de pesos customizados, altere o caminho abaixo
    return YOLO('yolov8n.pt')

_model = _load_model()


def detect(frame: np.ndarray):
    """
    Recebe um frame BGR (numpy.ndarray) e devolve lista de deteções:
    [
      { 'box': [x1, y1, x2, y2], 'label': str, 'conf': float },
      …
    ]
    """
    # Executa inferência
    results = _model(frame)[0]
    detections = []
    # Itera sobre as boxes retornadas (x1, y1, x2, y2, conf, cls)
    for *box, conf, cls in results.boxes.data.tolist():
        # Filtra apenas classes de gato (15) e cão (16) no COCO
        if int(cls) in (15, 16):
            label = 'gato' if int(cls) == 15 else 'cao'
            detections.append({
                'box': box,
                'label': label,
                'conf': float(conf)
            })
    return detections
