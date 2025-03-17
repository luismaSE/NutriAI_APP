from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MealModel(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    meal_data = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Meal {self.id}>'