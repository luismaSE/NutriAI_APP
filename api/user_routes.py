from flask import Blueprint, request, jsonify
from models.user import UserModel
from models.database import db
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Crea un nuevo usuario (registro).
    Entrada esperada: JSON con 'username'.
    Respuesta: JSON con mensaje y el ID del usuario creado.
    """
    try:
        username = request.json.get('username')
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        if UserModel.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409

        new_user = UserModel(id=str(uuid.uuid4().hex), username=username)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'id': new_user.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Obtiene los detalles del usuario autenticado.
    """
    try:
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': {'id': user.id, 'username': user.username}}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Actualiza el nombre de usuario, si pertenece al usuario autenticado.
    Entrada esperada: JSON con 'username'.
    """
    try:
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        new_username = request.json.get('username')
        if not new_username:
            return jsonify({'error': 'New username is required'}), 400
        if UserModel.query.filter_by(username=new_username).first():
            return jsonify({'error': 'Username already exists'}), 409
        user.username = new_username
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Elimina al usuario autenticado.
    """
    try:
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500