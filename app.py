from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests #type: ignore
import os
import json
import base64
import cv2
import numpy as np

from model.imageHandler import ImageHandler
from model.food import Meal , FoodFormater
from model.mealModel import MealModel
from model.database import db
app = Flask(__name__)

# Configuración

NUTRI_API_URL = os.getenv('NUTRI_API_URL')
NUTRI_MACROS_API_URL = os.getenv('NUTRI_MACROS_API_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals.db'  # Crea una base de datos SQLite llamada 'meals.db'
db.init_app(app)


food_formater = FoodFormater()
image_handler = ImageHandler()

# Crea la tabla si no existe
with app.app_context():
    db.create_all()

# FOOD DETECTION

@app.route('/image', methods=['POST'])
def process_image():
    try:
        # Verificar si se proporciona una imagen en la solicitud
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400

        # Obtener la imagen de la solicitud
        image = request.files['image']

        # Verificar el tipo de archivo y validar la extensión
        if not image.filename:
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        if not any(image.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Formato de imagen no admitido'}), 400

        # Leer los bytes de la imagen
        image_bytes = image.read()

        # Decodificar la imagen utilizando OpenCV
        image_cv = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

        # Verificar si la decodificación fue exitosa
        if image_cv is None:
            return jsonify({'error': 'No se pudo decodificar la imagen'}), 500

        # Enviar la imagen al API
        files = {'image': image_bytes}
        response = requests.post(NUTRI_API_URL, files=files)

        # Verificar el estado de la respuesta del API
        if response.status_code != 200:
            return jsonify({'error': 'Error al procesar la imagen en el API'}), 500

        # Procesar la respuesta del API
        response_data = response.json()
        if 'error' in response_data:
            return jsonify({'error': response_data['error']}), 500

        # Procesar la información del resultado
        try:
            macros_dict = json.loads(response_data['macros'])
            ingredients, cautions, diet_labels, health_labels = food_formater.process_json(macros_dict)
            meal = Meal(ingredients, cautions, diet_labels, health_labels)
            
            # Guardar la comida en la base de datos
            new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()))
            db.session.add(new_meal_model)
            db.session.commit()

        except:
            return jsonify({'error': 'Error al procesar los datos de la comida'}), 500

        # result = json.loads(response_data['result'])
        result = response_data['result']
        
        mod_image = image_handler.draw_polygons(image_cv, result)

        # Codificar la imagen modificada como base64
        img_encoded = cv2.imencode('.jpg', mod_image)[1]
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')

        return jsonify({'meal': meal.to_json(), 'image': img_base64}), 200
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

        # Verificar si la descarga fue exitosa
        if response.status_code != 200:
            return jsonify({'error': 'No se pudo descargar la imagen'}), 500

        # Enviar la imagen al API
        files = {'image': response.content}
        response = requests.post(NUTRI_API_URL, files=files)

        # Procesar la respuesta del API
        response_data = response.json()
        if 'error' in response_data:
            return jsonify({'error': response_data['error']}), 500

        # Procesar la información del resultado
        macros_dict = json.loads(response_data['macros'])
        ingredients, cautions, diet_labels, health_labels = food_formater.process_json(macros_dict)
        meal = Meal(ingredients, cautions, diet_labels, health_labels)
        # Guardar la comida en la base de datos
        new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()))
        db.session.add(new_meal_model)
        db.session.commit()

        return jsonify({'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500








#MEAL

@app.route('/new_meal', methods=['POST'])
def new_meal():
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna comida'}), 400

        meal = Meal.from_json(request.json) #type: ignore
        
        # Guardar la comida en la base de datos
        new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()))
        db.session.add(new_meal_model)
        db.session.commit()

        return jsonify({'message': 'Comida creada correctamente', 'id': meal.id}), 201
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/get_meal/<meal_id>', methods=['GET'])
def get_meal(meal_id: str):
    try:
        meal_model = MealModel.query.get(meal_id)
        if meal_model is None:
            return jsonify({'error': 'ID de comida no válido'}), 400

        meal_data = json.loads(meal_model.meal_data)
        meal = Meal.from_json(meal_data) #type: ignore
        return jsonify({'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500



@app.route('/update_meal/<meal_id>', methods=['PUT'])
def update_meal(meal_id: str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400

        meal_model = MealModel.query.get(meal_id)
        if meal_model is None:
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Actualizar la comida en la base de datos
        updated_meal_data = request.json['meal']
        meal_model.meal_data = json.dumps(updated_meal_data)  # Actualiza directamente los datos de la comida
        db.session.commit()

        return jsonify({'message': 'Comida actualizada correctamente', 'meal': updated_meal_data}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

    
    
    
    
    
#INGREDIENT
    
    
# El endpoint debe recibir un ingrediente con 'weight' modificado, no se puede modificar el nombre del ingrediente
# Una vez modificado el peso del ingrediente, se debe actualizar cada uno de los nutrientes de ese ingrediente y la comida en general    
      
@app.route('/update_ingredient/<meal_id>', methods=['PUT'])
def update_ingredient(meal_id: str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400

        meal_model = MealModel.query.get(meal_id)
        if meal_model is None:
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida existente de la base de datos
        meal_data = json.loads(meal_model.meal_data)
        meal = Meal.from_json(meal_data)  # Usar from_json para mantener la ID

        ingredient_name = str(request.json['ingredient_name'])
        print('name:',ingredient_name)
        weight = float(request.json['weight'])

        if not meal.update_ingredient(ingredient_name, weight, meal.get_ingredient(ingredient_name)):
            return jsonify({'error': 'Ingrediente no encontrado'}), 404

        # Actualizar la comida en la base de datos
        meal_model.meal_data = json.dumps(meal.to_json())
        db.session.commit()

        return jsonify({'message': 'Ingrediente actualizado correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        print('error:',e)
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/add_ingredient/<meal_id>', methods=['POST'])
def add_ingredient(meal_id: str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400

        meal_model = MealModel.query.get(meal_id)
        if meal_model is None:
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida existente de la base de datos
        meal_data = json.loads(meal_model.meal_data)
        meal = Meal.from_json(meal_data)  # Usar from_json para mantener la ID

        query = [f"{ingr.weight}g of {ingr.name}" for ingr in meal.ingredients]
        query.append(request.json['query'])
        print('query:',query)
        response = requests.post(NUTRI_MACROS_API_URL, json={'query': query})

        if response.status_code != 200:
            error_message = response.json().get('error', 'Error desconocido de la API')
            return jsonify({'error': f'Error de la API: {error_message}'}), response.status_code

        response_data = response.json()
        if 'error' in response_data:
            return jsonify({'error': f'Error de la API:{str(response_data["error"])}'}), 500
        macros_dict = response_data
        ingredients, cautions, diet_labels, health_labels = food_formater.process_json(macros_dict)

        # Actualizar la información nutricional de la comida EXISTENTE
        meal.ingredients = ingredients
        meal.cautions = cautions
        meal.diet_labels = diet_labels
        meal.health_labels = health_labels

        # Actualizar la comida en la base de datos
        meal_model.meal_data = json.dumps(meal.to_json())
        db.session.commit()
        return jsonify({'message': 'Ingrediente añadido correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

    

      
@app.route('/remove_ingredient/<meal_id>', methods=['DELETE'])
def remove_ingredient(meal_id: str):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400

        meal_model = MealModel.query.get(meal_id)
        if meal_model is None:
            return jsonify({'error': 'ID de comida no válido'}), 400

        # Obtener la comida existente de la base de datos
        meal_data = json.loads(meal_model.meal_data)
        meal = Meal.from_json(meal_data)

        # Eliminar el ingrediente
        ingredient_name = request.json['ingredient_name']
        if not meal.remove_ingredient_by_name(ingredient_name):
            return jsonify({'error': 'Ingrediente no encontrado'}), 404

        # Construir la nueva consulta con los ingredientes restantes
        query = [f"{ingr.weight}g of {ingr.name}" for ingr in meal.ingredients]

        # Enviar la consulta al API para recalcular los macros
        response = requests.post(NUTRI_MACROS_API_URL, json={'query': query})

        if response.status_code != 200:
            error_message = response.json().get('error', 'Error desconocido de la API')
            return jsonify({'error': f'Error de la API: {error_message}'}), response.status_code

        response_data = response.json()
        if 'error' in response_data:
            return jsonify({'error': f'Error de la API:{str(response_data["error"])}'}), 500
        macros_dict = response_data
        ingredients, cautions, diet_labels, health_labels = food_formater.process_json(macros_dict)

        # Actualizar la información nutricional de la comida EXISTENTE
        meal.ingredients = ingredients
        meal.cautions = cautions
        meal.diet_labels = diet_labels
        meal.health_labels = health_labels

        # Actualizar la comida en la base de datos
        meal_model.meal_data = json.dumps(meal.to_json())
        db.session.commit()

        return jsonify({'message': 'Ingrediente eliminado correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

    



if __name__ == '__main__':
    load_dotenv()
    # app.run(debug=True, port=5005)
    # app.run(debug=True, host='192.168.100.18', port=5005)
    app.run(debug=True, host='0.0.0.0', port=5005)
