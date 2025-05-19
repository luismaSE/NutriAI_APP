from flask import Flask
from config import Config
from models.database import db
from flask_jwt_extended import JWTManager

from api.routes import api_bp
from api.user_routes import user_bp
from api.meal_routes import meal_bp
from api.auth import auth_bp

# Inicializa la aplicación Flask
app = Flask(__name__)

# Carga la configuración desde la clase Config
app.config.from_object(Config)

# Inicializa la base de datos con la aplicación
db.init_app(app)

# Crea las tablas en la base de datos dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

# Configura la clave secreta y las opciones de JWT
app.config['SECRET_KEY'] = 'X7k9pL2mN8qR5tW3vY6zA1bC4dE7fG9h'  # Reemplaza con una clave segura generada
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Desactiva la expiración del token
jwt = JWTManager(app)

# Registra los blueprints para las rutas de la API
app.register_blueprint(api_bp)
app.register_blueprint(meal_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)

# Ejecuta la aplicación en modo desarrollo con soporte para concurrencia
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005, threaded=True)