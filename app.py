from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os
import json
import msgpack
import pickle
import base64
import cv2
import numpy as np

from model.imageHandler import ImageHandler
from model.food import Meal , Ingredient, FoodFormater

app = Flask(__name__)

# Configuración

NUTRI_API_URL = os.getenv('NUTRI_API_URL')

food_formater = FoodFormater()
image_handler = ImageHandler()
meals = {}


# FOOD DETECTION

@app.route('/image', methods=['POST'])
def process_image():
    try:
        # Verificar si se proporciona una imagen en la solicitud
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400

        # Obtener la imagen de la solicitud
        image = request.files['image']
        image_bytes = image.read()
        
        # Verificar el tipo de archivo
        if image.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            return jsonify({'error': 'Formato de imagen no admitido'}), 400

        # Convertir los bytes de la imagen en un array numpy
        nparr = np.frombuffer(image_bytes, np.uint8)

        # Decodificar la imagen utilizando OpenCV
        image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Verificar si la decodificación fue exitosa
        if image_cv is None:
            return jsonify({'error': 'No se pudo decodificar la imagen'}), 500

        # Enviar la imagen al API
        files = {'image': image_bytes}
        response = requests.post(NUTRI_API_URL, files=files)
        
        # Procesar la respuesta del API
        response_data = response.json()
        macros_dict = json.loads(response_data['macros'])
        ingredients, cautions, diet_labels, health_labels = food_formater.process_json(macros_dict)
        meal = Meal(ingredients, cautions, diet_labels, health_labels)
        meals[meal.id] = meal
                
        result = json.loads(response_data['result'])
        
        # Dibujar las cajas delimitadoras en la imagen
        mod_image = image_handler.draw_boxes(image_cv, result)

        # Codificar la imagen modificada como base64
        _, img_encoded = cv2.imencode('.jpg', mod_image)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')

        return jsonify({'meal': meal.to_json(),'image': img_base64}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/link', methods=['POST'])
def process_image_link():
    try:
        # Verificar si se proporciona una URL de imagen en la solicitud
        if 'image_link' not in request.json:
            return jsonify({'error': 'No se proporcionó ninguna URL de imagen'}), 400

        # Obtener la URL de la imagen de la solicitud
        image_link = request.json['image_link']

        # Descargar la imagen de la URL
        response = requests.get(image_link)
        image_bytes = response.content

        # Verificar si la descarga fue exitosa
        if response.status_code != 200:
            return jsonify({'error': 'No se pudo descargar la imagen'}), 500

        # Enviar la imagen al API
        files = {'image': image_bytes}
        response = requests.post(NUTRI_API_URL, files=files)

        # Procesar la respuesta del API
        response_data = response.json()
        macros_dict = json.loads(response_data['macros'])
        ingredients, cautions, diet_labels, health_labels = food_formater.process_json(macros_dict)
        meal = Meal(ingredients, cautions, diet_labels, health_labels)
        meals[meal.id] = meal
        
        
        result = json.loads(response_data['result'])

        return jsonify({'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    












#ABM MEAL

@app.route('/new_meal', methods=['POST'])
def new_meal():
    try:
        # Verificar si se proporciona una comida en la solicitud
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna comida'}), 400

        # Crear una nueva comida
        meal = Meal().from_json(request.json)
        meals[meal.id] = meal

        return jsonify({'message': 'Comida creada correctamente'}), 201
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    
@app.route('/get_meal/<meal_id>', methods=['GET'])
def get_meal(meal_id:str):
    try:
        # Verificar si el ID de la comida es válido
        if meal_id not in meals.keys():
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida correspondiente al ID
        meal = meals[meal_id]

        return jsonify({'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    
    
@app.route('/update_meal/<meal_id>', methods=['PUT'])
def update_meal(meal_id:str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        # Verificar si el ID de la comida es válido
        if meal_id not in meals.keys():
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida correspondiente al ID
        meal = meals[meal_id]
        
        # Actualizar los datos de la comida
        meal.update(request.json['meal'])
        meals[meal_id] = meal

        return jsonify({'message': 'Comida actualizada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    
@app.route('/delete_meal/<meal_id>', methods=['DELETE'])
def delete_meal(meal_id:str):
    try:
        # Verificar si el ID de la comida es válido
        if meal_id not in meals.keys():
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Eliminar la comida correspondiente al ID
        del meals[meal_id]

        return jsonify({'message': 'Comida eliminada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



#ABM INGREDIENT

@app.route('/add_ingredient/<meal_id>', methods=['POST'])
def add_ingredient(meal_id:str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        # Verificar si el ID de la comida es válido
        if meal_id not in meals.keys():
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida correspondiente al ID
        meal = meals[meal_id]
        
        # Crear un nuevo ingrediente
        ingredient = Ingredient().from_json(request.json['ingredient'])
        meal.add_ingredient(ingredient)
        meals[meal_id] = meal

        return jsonify({'message': 'Ingrediente añadido correctamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
@app.route('/remove_ingredient/<meal_id>', methods=['DELETE'])
def remove_ingredient(meal_id:str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        # Verificar si el ID de la comida es válido
        if meal_id not in meals.keys():
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida correspondiente al ID
        meal = meals[meal_id]
        
        # Eliminar el ingrediente
        ingredient_name = request.json['ingredient_name']
        if not meal.remove_ingredient_by_name(ingredient_name):
            return jsonify({'error': 'Ingrediente no encontrado'}), 404
        meals[meal_id] = meal

        return jsonify({'message': 'Ingrediente eliminado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
@app.route('/update_ingredient/<meal_id>', methods=['PUT'])
def update_ingredient(meal_id:str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        # Verificar si el ID de la comida es válido
        if meal_id not in meals.keys():
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida correspondiente al ID
        meal = meals[meal_id]
        
        # Actualizar el ingrediente
        ingredient_name = request.json['ingredient_name']
        ingredient = Ingredient().from_json(request.json['ingredient'])
        if not meal.update_ingredient(ingredient_name, ingredient):
            return jsonify({'error': 'Ingrediente no encontrado'}), 404
        meals[meal_id] = meal

        return jsonify({'message': 'Ingrediente actualizado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500








if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True, port=5005)
