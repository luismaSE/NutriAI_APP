import json
import uuid
from config import Config
from models.ingredient import Ingredient

class Meal:
    def __init__(self, ingredients: list, cautions: list, diet_labels: list, health_labels: list, rda: dict | None = None, id: str | None = None) -> None:
        self.id = id if id else uuid.uuid4().hex
        self.ingredients = ingredients
        self.cautions = cautions
        self.diet_labels = diet_labels
        self.health_labels = health_labels
        self.rda = rda if rda else self.load_rda()

    def __repr__(self):
        return f'<Meal {self.id}>'

    def load_rda(self):
        with open(Config.RDA_FILE_PATH, 'r') as f:
            rda = json.load(f)
        return rda["RDA"]

    def get_ingredient(self, ingredient_name: str):
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                return ingredient

    def add_ingredient(self, ingredient: Ingredient):
        self.ingredients.append(ingredient)

    def remove_ingredient_by_name(self, ingredient_name: str):
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                self.ingredients.remove(ingredient)
                return True
        return False

    def update_ingredient(self, ingredient_name: str, weight: float, orig_ingr: Ingredient):
        for ingr in self.ingredients:
            if ingr.name == ingredient_name:
                ingr.calories = (weight * ingr.calories) / ingr.weight
                for nutrient in ['protein', 'carbs', 'fibtg', 'fasat', 'fat', 'na', 'chole', 'sugar']:
                    attr = getattr(ingr, nutrient)
                    attr.quantity = (weight * attr.quantity) / ingr.weight
                ingr.weight = weight
                return True
        return False

    def total_nutritional_info(self) -> dict:
        total_calories = sum(ingredient.calories for ingredient in self.ingredients)
        total_protein = sum(ingredient.protein.quantity for ingredient in self.ingredients)
        total_carbs = sum(ingredient.carbs.quantity for ingredient in self.ingredients)
        total_fibtg = sum(ingredient.fibtg.quantity for ingredient in self.ingredients)
        total_fats = sum(ingredient.fat.quantity for ingredient in self.ingredients)
        total_sugar = sum(ingredient.sugar.quantity for ingredient in self.ingredients)
        total_na = sum(ingredient.na.quantity for ingredient in self.ingredients)
        return {
            "calories": total_calories,
            "fats": total_fats,
            "carbs": total_carbs,
            "protein": total_protein,
            "sugar": total_sugar,
            "na": total_na
        }

    def total_daily_info(self) -> dict:
        total_nutrients = self.total_nutritional_info()
        daily_nutritional_info = {}
        for nutrient, total_amount in total_nutrients.items():
            try:
                daily_nutritional_info[nutrient] = (total_amount / self.rda[nutrient]) * 100
            except KeyError:
                pass
        return daily_nutritional_info

    def to_json(self):
        return {
            'id': self.id,
            'ingredients': [ingredient.to_json() for ingredient in self.ingredients],
            'total_nutritional_info': self.total_nutritional_info(),
            'daily_nutritional_info': self.total_daily_info(),
            'cautions': self.cautions,
            'diet_labels': self.diet_labels,
            'health_labels': self.health_labels
        }

    @classmethod
    def from_json(cls, data: dict):
        ingredients = [Ingredient.from_json(i) for i in data['ingredients']]
        return cls(
            ingredients,
            data['cautions'],
            data['diet_labels'],
            data['health_labels'],
            data.get('rda'),
            data.get('id')
        )