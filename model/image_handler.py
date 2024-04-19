import os
import requests

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
