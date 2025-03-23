from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MealModel(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.String(32), primary_key=True)  # ID único para la comida
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)  # Relación con usuario
    meal_data = db.Column(db.Text, nullable=False)  # Datos de la comida en formato JSON

    user = db.relationship('UserModel', backref=db.backref('meals', lazy=True))

    def __repr__(self):
        return f'<Meal {self.id} for User {self.user_id}>'