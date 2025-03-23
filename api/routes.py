import json
from flask import Blueprint, request, jsonify
from api.services import ApiService
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.database import db
from models.database import MealModel
from models.meal import Meal
import requests
import uuid
from config import Config
from utils.food_formatter import FoodFormatter

api_bp = Blueprint('api', __name__)
api_service = ApiService()


@api_bp.route('/api/image', methods=['POST'])
@jwt_required()
def image():
    try:
        user_id = get_jwt_identity()
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400
        image = request.files['image']
        if not image.filename:
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        if not any(image.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Formato de imagen no admitido'}), 400

        image_bytes = image.read()
        print()
        api_service = ApiService()  # Instancia del servicio
        result = api_service.detect_foods(image_bytes, user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    
@api_bp.route('/get_macros', methods=['POST'])
@jwt_required()
def calculate_macros():
    try:
        user_id = get_jwt_identity()  # Obtiene el ID del usuario autenticado
        data = request.get_json()  # Recibe los datos enviados desde Flutter
        print(f"Data: {data}")
        if not data or 'query' not in data:
            return jsonify({'error': 'Se requiere una lista de consultas en "query"'}), 400

        # Extrae la lista de consultas enviada desde Flutter
        query = {"query": data['query']}  # Formato: {"query": ["1 serving of rice", "100g of meat", ...]}

        # Llama al endpoint /get_macros de la segunda API
        response = requests.post(
            f"{Config.NUTRI_API_URL}/get_macros",
            headers={'Content-Type': 'application/json'},
            json=query
        )
        response.raise_for_status()  # Lanza una excepción si falla

        # Obtiene los datos de la respuesta
        response_data = response.json()

        # Procesa la respuesta como en el bloque proporcionado (sin procesamiento de imagen)
        if 'error' in response_data:
            raise ValueError(response_data['error'])

        # Instancia el formateador de alimentos
        food_formatter = FoodFormatter()

        # Procesa los macronutrientes
        # print(f"Response data: {response_data}")
        # print(f"Macros: {type(response_data['macros'])}")
        # macros_dict = json.loads(response_data['macros'])  # Asume que 'macros' es una cadena JSON
        # print(f"Macros dict: {type(macros_dict)}")
        # print("conveti el json")
        macros_dict = response_data['macros']
        ingredients, cautions, diet_labels, health_labels = food_formatter.process_json(macros_dict)

        # Crea un objeto Meal
        meal = Meal(
            id=str(uuid.uuid4()),  # Genera un ID único
            ingredients=ingredients,
            cautions=cautions,
            diet_labels=diet_labels,
            health_labels=health_labels
        )

        # Guarda el meal en la base de datos
        new_meal_model = MealModel(
            id=meal.id,
            meal_data=json.dumps(meal.to_json()),
            user_id=user_id
        )
        db.session.add(new_meal_model)
        db.session.commit()

        # Devuelve el meal como JSON a Flutter
        print(f"Meal: {meal.to_json()}")
        return jsonify({'meal': meal.to_json()}), 200

    except requests.RequestException as e:
        return jsonify({'error': f'Error al consultar get_macros: {str(e)}'}), 500
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Error al calcular macros: {str(e)}'}), 500
    

@api_bp.route('/image_og', methods=['POST'])
@jwt_required()
def image_og():
    """
    Procesa una imagen subida por el usuario autenticado.
    Entrada esperada: Form-data con la clave 'image' (archivo de imagen).
    Respuesta: JSON con los datos de la comida y la imagen procesada en base64.
    """
    try:
        user_id = get_jwt_identity()
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400
        image = request.files['image']
        if not image.filename:
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        if not any(image.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Formato de imagen no admitido'}), 400
        image_bytes = image.read()
        result = api_service.process_image(image_bytes, user_id)
        print(result['meal'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/link', methods=['POST'])
@jwt_required()
def process_image_link():
    """
    Procesa una imagen desde un enlace proporcionado por el usuario autenticado.
    Entrada esperada: JSON con 'image_link'.
    Respuesta: JSON con los datos de la comida y la imagen procesada en base64.
    """
    try:
        user_id = get_jwt_identity()
        if 'image_link' not in request.json:
            return jsonify({'error': 'No se proporcionó ninguna URL de imagen'}), 400
        image_link = request.json['image_link']
        result = api_service.process_image_link(image_link, user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# import json
# from flask import Blueprint, request, jsonify
# from api.services import ApiService
# from models.user import UserModel

# api_bp = Blueprint('api', __name__)
# api_service = ApiService()

# @api_bp.route('/image', methods=['POST'])
# def image():
#     try:
#         user_id = request.form.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'User ID is required'}), 400

#         # Verificar si el usuario existe
#         user = UserModel.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         if 'image' not in request.files:
#             return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400
        
#         image = request.files['image']
        
#         if not image.filename:
#             return jsonify({'error': 'Nombre de archivo vacío'}), 400
#         allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        
#         if not any(image.filename.lower().endswith(ext) for ext in allowed_extensions):
#             return jsonify({'error': 'Formato de imagen no admitido'}), 400
        
#         image_bytes = image.read()
#         result = api_service.process_image(image_bytes, user_id)
#         return jsonify(result), 200
#     except Exception as e:
#         print(e)
#         return jsonify({'error': str(e)}), 500

# @api_bp.route('/link', methods=['POST'])
# def process_image_link():
#     try:
#         if 'image_link' not in request.json:
#             return jsonify({'error': 'No se proporcionó ninguna URL de imagen'}), 400
#         image_link = request.json['image_link']
#         result = api_service.process_image_link(image_link)
#         return jsonify(result), 200
#     except Exception as e:
#         print(e)
#         return jsonify({'error': str(e)}), 500