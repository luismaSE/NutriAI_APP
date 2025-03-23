from models.database import db  # Importa la instancia global de SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel(db.Model):
    __tablename__ = 'user_model'
    id = db.Column(db.Integer, primary_key=True)  # ID autoincremental
    username = db.Column(db.String(80), unique=True, nullable=False)  # Nombre de usuario único
    password_hash = db.Column(db.String(128), nullable=False)  # Hash de la contraseña

    def set_password(self, password):
        """Genera un hash seguro para la contraseña"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña coincide con el hash almacenado"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'