import json
from flask import Blueprint, request, jsonify
from api.services import ApiService
from models.database import MealModel, db
from flask_jwt_extended import jwt_required, get_jwt_identity

meal_bp = Blueprint('meal', __name__)
api_service = ApiService()

def get_user_id_as_int():
    """Convierte el user_id del token (string) a entero."""
    try:
        return int(get_jwt_identity())
    except ValueError:
        raise ValueError("ID de usuario inválido en el token")

@meal_bp.route('/meals', methods=['GET'])
@jwt_required()
def get_user_meals():
    try:
        user_id = get_user_id_as_int()
        meals = MealModel.query.filter_by(user_id=user_id).all()
        meals_data = []
        for meal in meals:
            meal_json = json.loads(meal.meal_data)
            meal_json['created_at'] = meal.created_at.isoformat()
            meal_json['image_base64'] = meal.image_base64
            meals_data.append(meal_json)
        print(meals_data)
        return jsonify({'meals': meals_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/meal/new_meal', methods=['POST'])
@jwt_required()
def new_meal():
    try:
        user_id = get_user_id_as_int()
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna comida'}), 400
        meal_data = request.json
        meal = api_service.create_meal(meal_data, user_id)
        return jsonify({'message': 'Comida creada correctamente', 'id': meal.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/get_meal/<meal_id>', methods=['GET'])
@jwt_required()
def get_meal(meal_id):
    try:
        user_id = get_user_id_as_int()
        meal = api_service.get_meal(meal_id)
        if meal.user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        return jsonify({'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/update_meal/<meal_id>', methods=['PUT'])
@jwt_required()
def update_meal(meal_id):
    try:
        user_id = get_user_id_as_int()
        meal = api_service.get_meal(meal_id)
        if meal.user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        updated_meal_data = request.json['meal']
        meal = api_service.update_meal(meal_id, updated_meal_data)
        return jsonify({'message': 'Comida actualizada correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/meal/update_ingredient/<meal_id>', methods=['PUT'])
@jwt_required()
def update_ingredient(meal_id):
    try:
        user_id = get_user_id_as_int()
        meal = api_service.get_meal(meal_id)
        if meal.user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        ingredient_name = request.json['ingredient_name']
        weight = request.json['weight']
        meal = api_service.update_ingredient(meal_id, ingredient_name, weight)
        return jsonify({'message': 'Ingrediente actualizado correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/meal/add_ingredient/<meal_id>', methods=['POST'])
@jwt_required()
def add_ingredient(meal_id):
    try:
        user_id = get_user_id_as_int()
        meal = api_service.get_meal(meal_id)
        if meal.user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        query = request.json['query']
        meal = api_service.add_ingredient(meal_id, query)
        return jsonify({'message': 'Ingrediente añadido correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/meal/remove_ingredient/<meal_id>', methods=['DELETE'])
@jwt_required()
def remove_ingredient(meal_id):
    try:
        user_id = get_user_id_as_int()
        meal = api_service.get_meal(meal_id)
        print(f"User ID from token: {user_id} <{type(user_id)}>")
        print(f"Meal User ID: {meal.user_id} <{type(meal.user_id)}>")
        if meal.user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        ingredient_name = request.json['ingredient_name']
        meal = api_service.remove_ingredient(meal_id, ingredient_name)
        return jsonify({'message': 'Ingrediente eliminado correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500