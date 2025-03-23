from flask import Blueprint, request, jsonify
from models.user import UserModel
from models.database import db
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username y password son obligatorios'}), 400

    # Verifica si el usuario ya existe
    if UserModel.query.filter_by(username=username).first():
        return jsonify({'error': 'El nombre de usuario ya existe'}), 409

    # Crea un nuevo usuario
    new_user = UserModel(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        user = UserModel.query.filter_by(username=username).first()
        if not user or not user.check_password(password):  # Asume que tienes un método check_password
            return jsonify({'error': 'Invalid credentials'}), 401
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500