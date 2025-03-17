from flask import Blueprint, request, jsonify
from api.services import ApiService

api_bp = Blueprint('api', __name__)
api_service = ApiService()

@api_bp.route('/image', methods=['POST'])
def image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400
        image = request.files['image']
        if not image.filename:
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        if not any(image.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Formato de imagen no admitido'}), 400
        image_bytes = image.read()
        result = api_service.process_image(image_bytes)
        return jsonify(result), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500




@api_bp.route('/link', methods=['POST'])
def process_image_link():
    try:
        if 'image_link' not in request.json:
            return jsonify({'error': 'No se proporcionó ninguna URL de imagen'}), 400
        image_link = request.json['image_link']
        result = api_service.process_image_link(image_link)
        return jsonify(result), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500



@api_bp.route('/new_meal', methods=['POST'])
def new_meal():
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna comida'}), 400
        meal_data = request.json
        meal = api_service.create_meal(meal_data)
        return jsonify({'message': 'Comida creada correctamente', 'id': meal.id}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@api_bp.route('/get_meal/<meal_id>', methods=['GET'])
def get_meal(meal_id):
    try:
        meal = api_service.get_meal(meal_id)
        return jsonify({'meal': meal.to_json()}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@api_bp.route('/update_meal/<meal_id>', methods=['PUT'])
def update_meal(meal_id):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        updated_meal_data = request.json['meal']
        meal = api_service.update_meal(meal_id, updated_meal_data)
        return jsonify({'message': 'Comida actualizada correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500



@api_bp.route('/update_ingredient/<meal_id>', methods=['PUT'])
def update_ingredient(meal_id):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        ingredient_name = request.json['ingredient_name']
        weight = request.json['weight']
        meal = api_service.update_ingredient(meal_id, ingredient_name, weight)
        return jsonify({'message': 'Ingrediente actualizado correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500



@api_bp.route('/add_ingredient/<meal_id>', methods=['POST'])
def add_ingredient(meal_id):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        query = request.json['query']
        meal = api_service.add_ingredient(meal_id, query)
        return jsonify({'message': 'Ingrediente añadido correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500



@api_bp.route('/remove_ingredient/<meal_id>', methods=['DELETE'])
def remove_ingredient(meal_id):
    try:
        if not request.json:
            return jsonify({'error': 'No se proporcionó ninguna solicitud JSON'}), 400
        ingredient_name = request.json['ingredient_name']
        meal = api_service.remove_ingredient(meal_id, ingredient_name)
        return jsonify({'message': 'Ingrediente eliminado correctamente', 'meal': meal.to_json()}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500