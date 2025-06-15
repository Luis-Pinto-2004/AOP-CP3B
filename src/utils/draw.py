# src/utils/draw.py
import cv2

def draw_boxes(frame, detections):
    for det in detections:
        x1,y1,x2,y2 = map(int, det['box'])
        text = f"{det['label']} {det['conf']:.2f}"
        color = (0,255,0) if det['label']=='gato' else (255,0,0)
        cv2.rectangle(frame,(x1,y1),(x2,y2), color, 2)
        cv2.putText(frame, text, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
