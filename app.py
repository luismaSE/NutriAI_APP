from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os
import json

from model.image_handler import ImageHandler
from model.food import Meal , Ingredient, FoodFormater

app = Flask(__name__)

# Configuración

NUTRI_API_URL = os.getenv('NUTRI_API_URL')
# PROCESSED_IMAGE_PATH = os.getenv('PROCESSED_IMAGE_PATH')

food_formater = FoodFormater()

@app.route('/send_image', methods=['POST'])
def process_image():
    try:
        # Verificar si se proporciona una imagen en la solicitud
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400

        # Obtener la imagen de la solicitud
        image = request.files['image']

        # Verificar el tipo de archivo
        if image.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg','.webp')):
            return jsonify({'error': 'Formato de imagen no admitido'}), 400

        # Procesar la imagen
        
        
        # Enviar la imagen procesada a una URL externa
        files = {'image': image}
        response = requests.post(NUTRI_API_URL, files=files)
        print(response.json()['macros'])
        print('voy a procesar los ingredientes')
        ingredients = food_formater.process_json(json.loads(response.json()['macros']))
        print('voy a crear la comida')
        meal = Meal(ingredients)
        print('he creado la comida')
        print(meal)

        #devolver la imagen y meal
        return jsonify({'image': response.json()['image'], 'meal': str(meal)}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True, port=5005)
