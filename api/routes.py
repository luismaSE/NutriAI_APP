import json
from flask import Blueprint, request, jsonify
from api.services import ApiService
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db, MealModel
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
        result = api_service.detect_foods(image_bytes, user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/get_macros', methods=['POST'])
@jwt_required()
def calculate_macros():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Se requiere una lista de consultas en "query"'}), 400

        query = {"query": data['query']}
        response = requests.post(
            f"{Config.NUTRI_API_URL}/get_macros",
            headers={'Content-Type': 'application/json'},
            json=query
        )
        response.raise_for_status()
        response_data = response.json()

        if 'error' in response_data:
            raise ValueError(response_data['error'])

        food_formatter = FoodFormatter()
        macros_dict = response_data['macros']
        ingredients, cautions, diet_labels, health_labels = food_formatter.process_json(macros_dict)

        meal = Meal(
            id=str(uuid.uuid4()),
            ingredients=ingredients,
            cautions=cautions,
            diet_labels=diet_labels,
            health_labels=health_labels
        )

        # Guardar sin incluir created_at ni image_base64 en meal_data
        meal_json = meal.to_json()
        del meal_json['created_at']  # Eliminar de meal_data
        del meal_json['image_base64']  # Eliminar de meal_data (es null aquí)
        new_meal_model = MealModel(
            id=meal.id,
            meal_data=json.dumps(meal_json),
            user_id=user_id,
            image_base64=None  # No hay imagen en esta ruta
        )
        db.session.add(new_meal_model)
        db.session.commit()

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
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/link', methods=['POST'])
@jwt_required()
def process_image_link():
    try:
        user_id = get_jwt_identity()
        if 'image_link' not in request.json:
            return jsonify({'error': 'No se proporcionó ninguna URL de imagen'}), 400
        image_link = request.json['image_link']
        result = api_service.process_image_link(image_link, user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500