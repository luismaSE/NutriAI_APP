import json
import os
import uuid

RDA_FILE_PATH = os.getenv('RDA_FILE_PATH', '/home/luisma_se/NUTRIAI/NutriAI_APP/config/default_rda.json')

class Nutrient:
    def __init__(self, label: str, quantity: float, unit: str) -> None:
        self.name = label
        self.amount = quantity
        self.unit = unit

    def __str__(self) -> str:
        return f"{self.name}: {self.amount} {self.unit}"

    def to_json(self):
        return {
            'label': self.name,
            'quantity': self.amount,
            'unit': self.unit
        }

    @classmethod
    def from_json(cls, data: dict):
        return cls(data['label'], data['quantity'], data['unit'])

class Ingredient:
    def __init__(self, name: str, weight: float, calories: float, protein: Nutrient, carbs: Nutrient, fibtg: Nutrient, 
                 fasat: Nutrient, fat: Nutrient, na: Nutrient, chole: Nutrient, sugar: Nutrient) -> None:
        self.name = name
        self.quantity = 1.0
        self.weight = weight
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fibtg = fibtg
        self.fasat = fasat
        self.fat = fat
        self.na = na
        self.chole = chole
        self.sugar = sugar

    def __str__(self) -> str:
        return (
            f"\n{self.name} ({self.weight} g):\n"
            f" {self.calories} kcal\n"
            f" {self.protein}\n"
            f" {self.carbs}\n"
            f" {self.fibtg}\n"
            f" {self.fasat}\n"
            f" {self.fat}\n"
            f" {self.na}\n"
            f" {self.chole}\n"
            f" {self.sugar}"
        )

    def to_json(self):
        return {
            'name': self.name,
            'weight': self.weight,
            'calories': self.calories,
            'protein': self.protein.to_json(),
            'carbs': self.carbs.to_json(),
            'fibtg': self.fibtg.to_json(),
            'fasat': self.fasat.to_json(),
            'fat': self.fat.to_json(),
            'na': self.na.to_json(),
            'chole': self.chole.to_json(),
            'sugar': self.sugar.to_json()
        }

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            data['name'],
            data['weight'],
            data['calories'],
            Nutrient.from_json(data['protein']),
            Nutrient.from_json(data['carbs']),
            Nutrient.from_json(data['fibtg']),
            Nutrient.from_json(data['fasat']),
            Nutrient.from_json(data['fat']),
            Nutrient.from_json(data['na']),
            Nutrient.from_json(data['chole']),
            Nutrient.from_json(data['sugar']),
        )

class Meal:
    def __init__(self, ingredients: list, cautions: list, diet_labels: list, health_labels: list, rda: dict | None = None, id: str | None = None) -> None:
        # Si se proporciona una ID en el JSON, úsala, de lo contrario, genera una nueva
        self.id = id if id else uuid.uuid4().hex 
        self.ingredients = ingredients
        self.cautions = cautions
        self.diet_labels = diet_labels
        self.health_labels = health_labels
        self.rda = rda if rda else self.load_rda()["RDA"]

    def load_rda(self):
        with open(RDA_FILE_PATH, 'r') as f:
            rda = json.load(f)
        return rda

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
        for i, ingr in enumerate(self.ingredients):
            if ingr.name == ingredient_name:
                # Actualiza calories directamente
                ingr.calories = (weight * ingr.calories) / ingr.weight 
                for nutrient in ['protein', 'carbs', 'fibtg', 'fasat', 'fat', 'na', 'chole', 'sugar']:
                    # Regla de 3 para actualizar los demás nutrientes
                    ingr.__getattribute__(nutrient).amount = (weight * ingr.__getattribute__(nutrient).amount) / ingr.weight
                ingr.weight = weight
                return True
        return False

    def total_nutritional_info(self) -> dict:
        total_calories = sum(ingredient.calories for ingredient in self.ingredients)
        total_protein = sum(ingredient.protein.amount for ingredient in self.ingredients)
        total_carbs = sum(ingredient.carbs.amount for ingredient in self.ingredients)
        total_fibtg = sum(ingredient.fibtg.amount for ingredient in self.ingredients)
        total_fats = sum(ingredient.fat.amount for ingredient in self.ingredients)
        total_sugar = sum(ingredient.sugar.amount for ingredient in self.ingredients)
        total_na = sum(ingredient.na.amount for ingredient in self.ingredients)
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

    def __str__(self) -> str:
        total_info = self.total_nutritional_info()
        info_str = "\nTotal Nutritional Information:\n"
        for nutrient, amount in total_info.items():
            info_str += f"{nutrient.capitalize()}: {amount:.2f}\n" # Formatea a dos decimales
        info_str += "\nDaily Nutritional Information:\n"
        daily_info = self.total_daily_info()
        for nutrient, amount in daily_info.items():
            info_str += f"{nutrient.capitalize()}: {amount:.2f}%\n" # Formatea a dos decimales
        info_str += "\nIngredients:\n"
        for ingredient in self.ingredients:
            info_str += f"\n{ingredient}"
        info_str += "\nCautions:\n"
        for caution in self.cautions:
            info_str += f"\n{caution}"
        info_str += "\nDiet Labels:\n"
        for diet_label in self.diet_labels:
            info_str += f"\n{diet_label}"
        info_str += "\nHealth Labels:\n"
        for health_label in self.health_labels:
            info_str += f"\n{health_label}"
        return info_str

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
        return cls(
            [Ingredient.from_json(i) for i in data['ingredients']],
            data['cautions'],
            data['diet_labels'],
            data['health_labels'],
            data.get('rda'),
            data.get('id')  # Pasa la ID del JSON al constructor
        )

    def update(self, data: dict):
        self.ingredients = [Ingredient.from_json(i) for i in data['ingredients']]
        self.cautions = data['cautions']
        self.diet_labels = data['diet_labels']
        self.health_labels = data['health_labels']
        return self

class FoodFormater:
    def load_json(self, file_path: str) -> dict:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data

    def process_json(self, data: dict) -> tuple:
        ingredients = []
        cautions = data['cautions']
        diet_labels = data['dietLabels']
        health_labels = data['healthLabels']
        for ingredient_data in data['ingredients']:
            ingredient_data = ingredient_data['parsed'][0]
            name = ingredient_data['food']
            calories = ingredient_data['nutrients']['ENERC_KCAL']['quantity']
            weight = ingredient_data['weight']
            ingr_nutrients = []
            for nutrient_name in ['PROCNT', 'CHOCDF', 'FIBTG', 'FASAT', 'FAT', 'NA', 'CHOLE', 'SUGAR']:
                try:
                    nutri_data = ingredient_data['nutrients'][nutrient_name]
                except KeyError:
                    nutri_data = {'label': nutrient_name, 'quantity': 0, 'unit': 'g'}
                ingr_nutrients.append(nutri_data)
            protein, carbs, fibtg, fasat, fat, na, chole, sugar = [
                Nutrient.from_json(nutri_data) for nutri_data in ingr_nutrients
            ]
            ingredient = Ingredient(name, weight, calories, protein, carbs, fibtg, fasat, fat, na, chole, sugar)
            ingredients.append(ingredient)
        return ingredients, cautions, diet_labels, health_labels

if __name__ == "__main__":
    food_formater = FoodFormater()
    json_data = food_formater.load_json('/home/luisma_se/NUTRIAI/NutriAI_APP/model/test.json')
    ingredient_objects, cautions, diet_labels, health_labels = food_formater.process_json(json_data)
    meal1 = Meal(ingredient_objects, cautions, diet_labels, health_labels)
    print(meal1)