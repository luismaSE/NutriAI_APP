import json , os

# RDA_FILE_PATH = os.getenv('RDA_FILE_PATH')
RDA_FILE_PATH = '/home/luisma_se/NUTRIAI/NutriAI_APP/config/default_rda.json'

class Nutrient:
    def __init__(self, nutrient) -> None:
        self.name = nutrient['label']
        self.amount = nutrient['quantity']
        self.unit = nutrient['unit']

    def __str__(self) -> str:
        return f"{self.name}: {self.amount} {self.unit}"
    
    
    
class Ingredient:
    def __init__(self , name:str , weight:float , calories:float  , protein:dict ,carbs:dict ,fibtg:dict ,fasat:dict ,fat:dict ,na:dict ,chole:dict ,sugar:dict) -> None:
        self.name = name
        self.quantity = 1.0
        self.weight = weight
        self.calories = calories
        
        self.protein = Nutrient(protein)
        self.carbs = Nutrient(carbs)
        self.fibtg = Nutrient(fibtg)
        
        self.fasat = Nutrient(fasat)
        # self.fatrn = Nutrient(fatrn)
        self.fat = Nutrient(fat)
        
        self.na = Nutrient(na)
        self.chole = Nutrient(chole)
        self.sugar = Nutrient(sugar)
        

    def __str__(self) -> str:
        return f"{self.name} ({self.weight} g): {self.calories} kcal\n {self.protein}\n {self.carbs}\n {self.fibtg}\n {self.fasat}\n {self.fat}\n {self.na}\n {self.chole}\n {self.sugar}"




class Meal:
    def __init__(self, ingredients, rda:str|None=None) -> None:
        self.ingredients = ingredients
        self.rda = rda if rda else self.load_rda()["RDA"]
    
    def load_rda(self):
        with open(RDA_FILE_PATH, 'r') as f:
            rda = json.load(f)
        return rda

    def total_nutritional_info(self) -> dict:
        # Cálculo de la información nutricional total
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

    def total_daily_nutritional_info(self) -> dict:
        # Cálculo de los porcentajes de la ingesta diaria recomendada (RDA)
        total_nutrients = self.total_nutritional_info()
        daily_nutritional_info = {}
        for nutrient, total_amount in total_nutrients.items():
            try:
                daily_nutritional_info[nutrient] = (total_amount / self.rda[nutrient]) * 100
            except KeyError:
                pass
        return daily_nutritional_info

    def daily_nutritional_info(self) -> str:
        # Mostrar los valores diarios de ingesta de nutrientes
        daily_info = self.total_daily_nutritional_info()
        info_str = "\nDaily Nutritional Information:\n"
        for nutrient, percentage in daily_info.items():
            info_str += f"{nutrient.capitalize()}: {percentage:.2f}%\n"
        return info_str

    def __str__(self) -> str:
        total_info = self.total_nutritional_info()
        info_str = "\nTotal Nutritional Information:\n"
        for nutrient, amount in total_info.items():
            info_str += f"{nutrient.capitalize()}: {amount}\n"
        info_str += self.daily_nutritional_info()
        for ingredient in self.ingredients:
            info_str += f"\n{ingredient}"
        
        return info_str


    


class FoodFormater:

    def load_json(self,file_path:str) -> dict:
        with open(file_path, 'r') as f:
            data = json.load(f)
        self.data = data
        return data

    def process_json(self,data:dict) -> list:
        self.data = data
        ingredients = []
        for ingredient_data in data['ingredients']:
            ingredient_data = ingredient_data['parsed'][0]
            name     = ingredient_data['food']
            calories = ingredient_data['nutrients']['ENERC_KCAL']['quantity']
            weight = ingredient_data['weight']
            quantity = ingredient_data['quantity']
            ingr_nutrients = []
            for nutrient in ['PROCNT','CHOCDF','FIBTG','FASAT','FAT','NA','CHOLE','SUGAR']:
                try:
                    nutri_data = ingredient_data['nutrients'][nutrient]
                    ingr_nutrients.append(nutri_data)
                except:
                    ingr_nutrients.append({'label':nutrient,'quantity':0,'unit':'g'})
                    
            protein,carbs,fibtg,fasat,fat,na,chole,sugar = ingr_nutrients
            # protein  = ingredient_data['nutrients']['PROCNT']
            # carbs    = ingredient_data['nutrients']['CHOCDF']
            # fibtg    = ingredient_data['nutrients']['FIBTG']
            
            # fasat     = ingredient_data['nutrients']['FASAT']
            # fat     = ingredient_data['nutrients']['FAT']
            # # fatrn     = ingredient_data['nutrients']['FATRN']
            
            
            # na       = ingredient_data['nutrients']['NA']
            # chole    = ingredient_data['nutrients']['CHOLE']
            # sugar    = ingredient_data['nutrients']['SUGAR']
            
            
        
        
        
            ingredient = Ingredient(name,weight,calories, 
                                protein,carbs,fibtg, 
                                fasat,fat,
                                # fatrn,
                                na,chole,sugar
                                )
        
            ingredients.append(ingredient)
    
        return ingredients

if __name__ == "__main__":
    pass

    # Ejemplo de uso
    food_formater = FoodFormater()
    json_data = food_formater.load_json('/home/luisma_se/NUTRIAI/NutriAI_APP/model/test.json')
    print(json_data)
    ingredient_objects = food_formater.process_json(json_data)
    meal1 = Meal(ingredient_objects)

    print(meal1)
    # print(meal1.daily_nutritional_info())

