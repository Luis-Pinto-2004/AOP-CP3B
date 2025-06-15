import numpy as np
import torch
from ultralytics import YOLO
import ultralytics.nn.tasks
from torch import serialization

# --- Monkey‐patch para compatibilidade com diferentes versões de torch.serialization ---
if not hasattr(serialization, 'add_safe_globals'):
    def add_safe_globals(globals_list):
        # stub: confiar nos pesos que estamos a carregar
        return None
    serialization.add_safe_globals = add_safe_globals

if not hasattr(serialization, 'safe_globals'):
    class _SafeGlobalsCM:
        def __init__(self, globs): pass
        def __enter__(self): pass
        def __exit__(self, exc_type, exc_val, exc_tb): return False
    serialization.safe_globals = lambda globs: _SafeGlobalsCM(globs)
# --- Fim do monkey‐patch ---

# Whitelist da classe DetectionModel para o carregamento seguro
serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])

def _load_model():
    """
    Carrega o modelo YOLO uma única vez, garantindo que a classe
    DetectionModel está na whitelist de globals do pickle.
    """
    # Se tiveres pesos customizados, altera o caminho aqui:
    return YOLO('yolov8n.pt')

# Instância global do modelo
_model = _load_model()

def detect(frame: np.ndarray):
    """
    Executa inferência num frame BGR (numpy.ndarray) e retorna lista de deteções:
      [
        { 'box': [x1, y1, x2, y2], 'label': str, 'conf': float },
        …
      ]
    Apenas deteta gato (cls 15) e cão (cls 16) do COCO.
    """
    results = _model(frame)[0]
    detections = []
    for *box, conf, cls in results.boxes.data.tolist():
        cls_id = int(cls)
        if cls_id in (15, 16):
            label = 'gato' if cls_id == 15 else 'cao'
            detections.append({
                'box': box,
                'label': label,
                'conf': float(conf)
            })
    return detections
