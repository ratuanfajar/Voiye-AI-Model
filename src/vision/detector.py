"""Detector: load YOLO model and run inference on images to detect vehicles"""

from ultralytics import YOLO
import cv2
import numpy as np

class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt"):
        print(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)
        # Target Classes (COCO): 2=Car, 5=Bus, 7=Truck
        self.target_classes = [2, 5, 7]

    def detect_potential_vehicle(self, image_bytes, threshold=0.5):
        """
        Mendeteksi apakah ada kendaraan target di gambar.
        Input: bytes gambar (dari upload file FastAPI).
        Output: (Found: bool, Message: str, Image: cv2_object)
        """
        # 1. Convert Bytes ke OpenCV Image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 2. Lakukan Prediksi
        results = self.model.predict(
            img, 
            conf=threshold, 
            classes=self.target_classes, 
            verbose=False
        )
        
        # 3. Cek Hasil
        if len(results) > 0 and len(results[0].boxes) > 0:
            # Ambil deteksi pertama (paling yakin)
            box = results[0].boxes[0]
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            
            return True, f"Detected {label}", img

        return False, "No target vehicle detected", img