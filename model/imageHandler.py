import os
import requests
from ultralytics.utils.plotting import Annotator, colors
import cv2
import numpy as np


class ImageHandler:
    def __init__(self):
        # Puedes inicializar cualquier configuración necesaria aquí
        pass

    def load_image_from_gallery(self, image_path):
        # Método para cargar una imagen desde la galería
        pass

    def capture_photo(self):
        # Método para capturar una foto con la cámara
        pass

    def process_image(self, image):
        # Método para procesar la imagen si es necesario
        pass

    def send_image(self, image , url):
        files = {'image': image}
        response = requests.post(url, files=files)
        return response

    def draw_boxes(self,tmp_image, result):
        color = (255, 255, 0)  # Color para las bounding boxes
        for item in result:
            class_name = item["name"]
            class_id = item["class"]
            conf = round(item["confidence"], 2)
            box = item["box"]
            x1, y1, x2, y2 = int(box["x1"]), int(box["y1"]), int(box["x2"]), int(box["y2"])
            
            # Dibujar la bounding box
            cv2.rectangle(tmp_image, (x1, y1), (x2, y2), color, 2)
            
            # Agregar etiqueta y confianza
            label = f'{class_name}: {conf}'
            cv2.putText(tmp_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return tmp_image


    # def draw_boxes(self, tmp_image, result):
    #     color = (255, 255,0)  # Color para las bounding boxes        
    #     for box in result.boxes:
    #         class_id = result.names[box.cls[0].item()]
    #         cords = box.xyxy[0].tolist()
    #         cords = [round(x) for x in cords]
    #         conf = round(box.conf[0].item(), 2)
    #         cv2.rectangle(tmp_image, (cords[0], cords[1]), (cords[2], cords[3]), color, 2)
    #         cv2.putText(tmp_image, f'{class_id}: {conf}', (cords[0], cords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    #     return tmp_image
