from models.ingredient import Ingredient
from models.nutrient import Nutrient

class FoodFormatter:
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