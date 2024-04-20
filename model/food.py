import json , os , uuid

# RDA_FILE_PATH = os.getenv('RDA_FILE_PATH')
RDA_FILE_PATH = '/home/luisma_se/NUTRIAI/NutriAI_APP/config/default_rda.json'

class Nutrient:
    def __init__(self, nutrient) -> None:
        self.name = nutrient['label']
        self.amount = nutrient['quantity']
        self.unit = nutrient['unit']

    def __str__(self) -> str:
        return f"{self.name}: {self.amount} {self.unit}"
    
    def to_json(self):
        return {
            'label':self.name,
            'quantity':self.amount,
            'unit':self.unit
        }
    
    def from_json(self,data:dict):
        return Nutrient(data['label'],data['quantity'],data['unit'])
    
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
        return f"\n{self.name} ({self.weight} g):\n {self.calories} kcal\n {self.protein}\n {self.carbs}\n {self.fibtg}\n {self.fasat}\n {self.fat}\n {self.na}\n {self.chole}\n {self.sugar}"

    def to_json(self):
        return {
            'name':self.name,
            'weight':self.weight,
            'calories':self.calories,
            'protein':self.protein.to_json(),
            'carbs':self.carbs.to_json(),
            'fibtg':self.fibtg.to_json(),
            'fasat':self.fasat.to_json(),
            'fat':self.fat.to_json(),
            'na':self.na.to_json(),
            'chole':self.chole.to_json(),
            'sugar':self.sugar.to_json()
        }
    
    @staticmethod
    def from_json(self,data:dict):
        return Ingredient(data['name'],data['weight'],data['calories'],data['protein'],data['carbs'],data['fibtg'],data['fasat'],data['fat'],data['na'],data['chole'],data['sugar'])


class Meal:
    def __init__(self, ingredients:list, cautions:list , diet_labels:list , health_labels:list, rda:str|None=None) -> None:
        #generate unique id
        self.id = uuid.uuid4().hex
        self.ingredients = ingredients
        self.cautions = cautions
        self.diet_labels = diet_labels
        self.health_labels = health_labels
        self.rda = rda if rda else self.load_rda()["RDA"]
    
    def load_rda(self):
        with open(RDA_FILE_PATH, 'r') as f:
            rda = json.load(f)
        return rda
    
    def add_ingredient(self, ingredient:Ingredient):
        self.ingredients.append(ingredient)
        
    def remove_ingredient_by_name(self,ingredient_name:str):
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                self.ingredients.remove(ingredient)
                return True
        return False
    
    def update_ingredient(self,ingredient_name:str,ingredient:Ingredient):
        for i,ingr in enumerate(self.ingredients):
            if ingr.name == ingredient_name:
                self.ingredients[i] = ingredient
                return True
        return False
        
        

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

    def total_daily_info(self) -> dict:
        # Cálculo de los porcentajes de la ingesta diaria recomendada (RDA)
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
            info_str += f"{nutrient.capitalize()}: {amount}\n"
        info_str += "\nDaily Nutritional Information:\n"
        daily_info = self.total_daily_info()
        for nutrient, amount in daily_info.items():
            info_str += f"{nutrient.capitalize()}: {amount}%\n"
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
            'id':self.id,
            'ingredients':[ingredient.to_json() for ingredient in self.ingredients],
            'total_nutritional_info':self.total_nutritional_info(),
            'daily_nutritional_info':self.total_daily_info(),
            'cautions':self.cautions,
            'diet_labels':self.diet_labels,
            'health_labels':self.health_labels
        }
        
    # def from_json(self,data:dict):
        # ingredients = [Ingredient(data['name'],data['weight'],data['calories'],data['protein'],data['carbs'],data['fibtg'],data['fasat'],data['fat'],data['na'],data['chole'],data['sugar']) for data in data['ingredients']]
        # return Meal(ingredients,data['cautions'],data['diet_labels'],data['health_labels'])
    
    def update(self,data:dict):
        self.ingredients = [Ingredient(data['name'],data['weight'],data['calories'],data['protein'],data['carbs'],data['fibtg'],data['fasat'],data['fat'],data['na'],data['chole'],data['sugar']) for data in data['ingredients']]
        self.cautions = data['cautions']
        self.diet_labels = data['diet_labels']
        self.health_labels = data['health_labels']
        return self


class FoodFormater:

    def load_json(self,file_path:str) -> dict:
        with open(file_path, 'r') as f:
            data = json.load(f)
        self.data = data
        return data

    def process_json(self,data:dict) -> list:
        self.data = data
        ingredients = []
        cautions = data['cautions']
        diet_labels = data['dietLabels']
        health_labels = data['healthLabels']
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
            
            
        
            ingredient = Ingredient(name,weight,calories, 
                                protein,carbs,fibtg, 
                                fasat,fat,
                                # fatrn,
                                na,chole,sugar
                                )
        
            ingredients.append(ingredient)
    
        return ingredients , cautions , diet_labels , health_labels

if __name__ == "__main__":
    pass

    # Ejemplo de uso
    food_formater = FoodFormater()
    json_data = food_formater.load_json('/home/luisma_se/NUTRIAI/NutriAI_APP/model/test.json')
    print(json_data)
    ingredient_objects,cautions , diet_labels , health_labels = food_formater.process_json(json_data)
    meal1 = Meal(ingredient_objects,cautions , diet_labels , health_labels)

    print(meal1)
    # print(meal1.health_labels)
    # print(meal1.diet_labels)
    # print(meal1.cautions)
    # print(meal1.daily_nutritional_info())

