# anti_spoofing.py
import math
from ultralytics import YOLO

class LivenessDetector:
    def __init__(self, model_path="models/l_version_1_300.pt", confidence=0.6):
        # Load YOLO model once
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.classNames = ["fake", "real"]

    def check_liveness(self, img):
        # Run YOLO inference with optimized image size (320) for speed
        results = self.model.predict(img, stream=True, verbose=False, imgsz=320)
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = math.ceil((box.conf[0] * 100)) / 100
                if conf > self.confidence:
                    cls = int(box.cls[0])
                    
                    # Extract face bounding box coordinates (x1, y1, x2, y2)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    return cls, conf, (x1, y1, x2, y2)
                    
        # Return defaults if no face detected or confidence is too low
        return -1, 0.0, None