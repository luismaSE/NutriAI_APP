# Modelo de la base de datos para Meal
from model.database import db

class MealModel(db.Model):  # type: ignore
    id = db.Column(db.String, primary_key=True)
    meal_data = db.Column(db.Text) # Almacenaremos el JSON de Meal aquí
