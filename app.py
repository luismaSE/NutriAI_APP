from flask import Flask
from config import Config
from models.database import db
from flask_jwt_extended import JWTManager

from api.routes import api_bp
from api.user_routes import user_bp
from api.meal_routes import meal_bp
from api.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Crea las tablas en la base de datos
with app.app_context():
    db.create_all()

app.config['SECRET_KEY'] = 'X7k9pL2mN8qR5tW3vY6zA1bC4dE7fG9h'  # Reemplaza con tu clave generada
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Desactiva la expiración del token
jwt = JWTManager(app)

# Registra los blueprints
app.register_blueprint(api_bp)
app.register_blueprint(meal_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)