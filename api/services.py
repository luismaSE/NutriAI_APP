import uuid
import requests
import json
import base64
import cv2
import numpy as np
from models.meal import Meal
from models.database import db, MealModel
from utils.image_handler import ImageHandler
from utils.food_formatter import FoodFormatter
from config import Config

class ApiService:
    def __init__(self):
        self.image_handler = ImageHandler()
        self.food_formatter = FoodFormatter()

    def process_image(self, image_bytes, user_id):
        try:
            image_cv = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            if image_cv is None:
                raise ValueError("No se pudo decodificar la imagen")

            files = {'image': image_bytes}
            response = requests.post(Config.NUTRI_API_URL, files=files)
            response.raise_for_status()
            response_data = response.json()

            if 'error' in response_data:
                raise ValueError(response_data['error'])

            macros_dict = json.loads(response_data['macros'])
            ingredients, cautions, diet_labels, health_labels = self.food_formatter.process_json(macros_dict)
            meal = Meal(ingredients, cautions, diet_labels, health_labels)

            new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()), user_id=user_id)
            db.session.add(new_meal_model)
            db.session.commit()

            result = response_data['result']
            mod_image = self.image_handler.draw_polygons(image_cv, result)
            if mod_image is None:
                raise ValueError("Error al dibujar los polígonos en la imagen")

            img_encoded = cv2.imencode('.jpg', mod_image)[1]
            img_base64 = base64.b64encode(img_encoded).decode('utf-8')

            return {'meal': meal.to_json(), 'image': img_base64}
        except Exception as e:
            raise e
        
        
    def detect_foods(self, image_bytes, user_id):
        """
        Detecta alimentos en una imagen y devuelve los nombres detectados junto con la imagen procesada.
        """
        try:
            # Decodifica la imagen
            image_cv = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            if image_cv is None:
                raise ValueError("No se pudo decodificar la imagen")

            # Envía la imagen a la API externa para detección
            files = {'image': image_bytes}
            response = requests.post(Config.NUTRI_API_URL+'/detect_food', files=files)
            response.raise_for_status()
            response_data = response.json()

            if 'error' in response_data:
                raise ValueError(response_data['error'])

            # Extrae los resultados de detección (nombres de alimentos)
            result = response_data['result']  # Asumo que 'result' contiene las detecciones
            detected_foods = [item.get('name') for item in result]  # Ajusta según la estructura real

            # Dibuja polígonos en la imagen
            mod_image = self.image_handler.draw_polygons(image_cv, result)
            if mod_image is None:
                raise ValueError("Error al dibujar los polígonos en la imagen")

            # Codifica la imagen procesada en base64
            img_encoded = cv2.imencode('.jpg', mod_image)[1]
            img_base64 = base64.b64encode(img_encoded).decode('utf-8')

            # Devuelve los alimentos detectados y la imagen procesada
            return {
                'detected_foods': detected_foods,
                'image': img_base64
            }

        except Exception as e:
            raise e

    def calculate_macros_from_foods(self, detected_foods, user_id):
        """
        Calcula los macronutrientes de los alimentos detectados usando /get_macros.
        """
        try:
            # Prepara la consulta para /get_macros
            query = {
                "query": detected_foods  # Lista de nombres de alimentos
            }

            # Llama al endpoint /get_macros
            response = requests.post(
                f"{Config.NUTRI_API_URL}/get_macros",
                headers={'Content-Type': 'application/json'},
                json=query
            )
            response.raise_for_status()
            response_data = response.json()

            # Procesa los macronutrientes
            macros_dict = json.loads(response_data['macros'])  # Ajusta según la respuesta real
            ingredients, cautions, diet_labels, health_labels = self.food_formatter.process_json(macros_dict)

            # Crea un objeto Meal
            meal = Meal(
                id=str(uuid.uuid4()),
                ingredients=ingredients,
                cautions=cautions,
                diet_labels=diet_labels,
                health_labels=health_labels,
                total_nutritional_info={},  # Ajusta según sea necesario
                daily_nutritional_info={}   # Ajusta según sea necesario
            )

            # Guarda en la base de datos
            new_meal_model = MealModel(
                id=meal.id,
                meal_data=json.dumps(meal.to_json()),
                user_id=user_id
            )
            db.session.add(new_meal_model)
            db.session.commit()

            return meal.to_json()

        except Exception as e:
            raise e
        

    def process_image_link(self, image_link, user_id):
        try:
            response = requests.get(image_link)
            if response.status_code != 200:
                raise ValueError("No se pudo descargar la imagen")
            image_bytes = response.content
            return self.process_image(image_bytes, user_id)
        except Exception as e:
            raise e

    def create_meal(self, meal_data, user_id):
        try:
            meal = Meal.from_json(meal_data)
            new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()), user_id=user_id)
            db.session.add(new_meal_model)
            db.session.commit()
            return meal
        except Exception as e:
            raise e

    def get_meal(self, meal_id):
        try:
            meal_model = MealModel.query.get(meal_id)
            if meal_model is None:
                raise ValueError("ID de comida no válido")
            meal_data = json.loads(meal_model.meal_data)
            meal = Meal.from_json(meal_data)
            meal.user_id = meal_model.user_id  # Añadimos user_id al objeto Meal para verificación
            return meal
        except Exception as e:
            raise e

    def update_meal(self, meal_id, updated_meal_data):
        try:
            meal_model = MealModel.query.get(meal_id)
            if meal_model is None:
                raise ValueError("ID de comida no válido")
            meal = Meal.from_json(updated_meal_data)
            meal_model.meal_data = json.dumps(meal.to_json())
            db.session.commit()
            return meal
        except Exception as e:
            raise e

    def update_ingredient(self, meal_id, ingredient_name, weight):
        try:
            meal_model = MealModel.query.get(meal_id)
            if meal_model is None:
                raise ValueError("ID de comida no válido")
            meal_data = json.loads(meal_model.meal_data)
            meal = Meal.from_json(meal_data)
            orig_ingr = meal.get_ingredient(ingredient_name)
            if not orig_ingr:
                raise ValueError("Ingrediente no encontrado")
            if not meal.update_ingredient(ingredient_name, weight, orig_ingr):
                raise ValueError("Error al actualizar el ingrediente")
            meal_model.meal_data = json.dumps(meal.to_json())
            db.session.commit()
            return meal
        except Exception as e:
            raise e

    def add_ingredient(self, meal_id, query):
        try:
            meal_model = MealModel.query.get(meal_id)
            if meal_model is None:
                raise ValueError("ID de comida no válido")
            meal_data = json.loads(meal_model.meal_data)
            meal = Meal.from_json(meal_data)
            query_list = [f"{ingr.weight}g of {ingr.name}" for ingr in meal.ingredients]
            query_list.append(query)
            response = requests.post(Config.NUTRI_MACROS_API_URL, json={'query': query_list})
            response.raise_for_status()
            response_data = response.json()
            if 'error' in response_data:
                raise ValueError(response_data['error'])
            macros_dict = response_data
            ingredients, cautions, diet_labels, health_labels = self.food_formatter.process_json(macros_dict)
            meal.ingredients = ingredients
            meal.cautions = cautions
            meal.diet_labels = diet_labels
            meal.health_labels = health_labels
            meal_model.meal_data = json.dumps(meal.to_json())
            db.session.commit()
            return meal
        except Exception as e:
            raise e

    def remove_ingredient(self, meal_id, ingredient_name):
        try:
            meal_model = MealModel.query.get(meal_id)
            if meal_model is None:
                raise ValueError("ID de comida no válido")
            meal_data = json.loads(meal_model.meal_data)
            meal = Meal.from_json(meal_data)
            if not meal.remove_ingredient_by_name(ingredient_name):
                raise ValueError("Ingrediente no encontrado")
            query_list = [f"{ingr.weight}g of {ingr.name}" for ingr in meal.ingredients]
            response = requests.post(Config.NUTRI_MACROS_API_URL, json={'query': query_list})
            response.raise_for_status()
            response_data = response.json()
            if 'error' in response_data:
                raise ValueError(response_data['error'])
            macros_dict = response_data
            ingredients, cautions, diet_labels, health_labels = self.food_formatter.process_json(macros_dict)
            meal.ingredients = ingredients
            meal.cautions = cautions
            meal.diet_labels = diet_labels
            meal.health_labels = health_labels
            meal_model.meal_data = json.dumps(meal.to_json())
            db.session.commit()
            return meal
        except Exception as e:
            raise e



# import requests
# import json
# import base64
# import cv2
# import numpy as np
# from models.meal import Meal
# from models.database import db, MealModel
# from utils.image_handler import ImageHandler
# from utils.food_formatter import FoodFormatter
# from config import Config

# class ApiService:
#     def __init__(self):
#         self.image_handler = ImageHandler()
#         self.food_formatter = FoodFormatter()

#     def process_image(self, image_bytes,user_id):
#         try:
#             image_cv = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
#             if image_cv is None:
#                 raise ValueError("No se pudo decodificar la imagen")

#             files = {'image': image_bytes}
#             response = requests.post(Config.NUTRI_API_URL, files=files)
#             response.raise_for_status()
#             response_data = response.json()

#             if 'error' in response_data:
#                 raise ValueError(response_data['error'])

#             macros_dict = json.loads(response_data['macros'])
#             ingredients, cautions, diet_labels, health_labels = self.food_formatter.process_json(macros_dict)
#             meal = Meal(ingredients, cautions, diet_labels, health_labels)

#             # new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()))
#             new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()), user_id=user_id)
#             db.session.add(new_meal_model)
#             db.session.commit()

#             result = response_data['result']
#             mod_image = self.image_handler.draw_polygons(image_cv, result)
#             if mod_image is None:
#                 raise ValueError("Error al dibujar los polígonos en la imagen")

#             img_encoded = cv2.imencode('.jpg', mod_image)[1]
#             img_base64 = base64.b64encode(img_encoded).decode('utf-8')

#             return {'meal': meal.to_json(), 'image': img_base64}
#         except Exception as e:
#             raise e
        
        

#     def process_image_link(self, image_link):
#         try:
#             response = requests.get(image_link)
#             if response.status_code != 200:
#                 raise ValueError("No se pudo descargar la imagen")
#             image_bytes = response.content
#             return self.process_image(image_bytes)
#         except Exception as e:
#             raise e

#     def create_meal(self, meal_data):
#         try:
#             meal = Meal.from_json(meal_data)
#             new_meal_model = MealModel(id=meal.id, meal_data=json.dumps(meal.to_json()))
#             db.session.add(new_meal_model)
#             db.session.commit()
#             return meal
#         except Exception as e:
#             raise e

#     def get_meal(self, meal_id):
#         try:
#             meal_model = MealModel.query.get(meal_id)
#             if meal_model is None:
#                 raise ValueError("ID de comida no válido")
#             meal_data = json.loads(meal_model.meal_data)
#             meal = Meal.from_json(meal_data)
#             return meal
#         except Exception as e:
#             raise e

#     def update_meal(self, meal_id, updated_meal_data):
#         try:
#             meal_model = MealModel.query.get(meal_id)
#             if meal_model is None:
#                 raise ValueError("ID de comida no válido")
#             meal = Meal.from_json(updated_meal_data)
#             meal_model.meal_data = json.dumps(meal.to_json())
#             db.session.commit()
#             return meal
#         except Exception as e:
#             raise e

#     def update_ingredient(self, meal_id, ingredient_name, weight):
#         try:
#             meal_model = MealModel.query.get(meal_id)
#             if meal_model is None:
#                 raise ValueError("ID de comida no válido")
#             meal_data = json.loads(meal_model.meal_data)
#             meal = Meal.from_json(meal_data)
#             orig_ingr = meal.get_ingredient(ingredient_name)
#             if not orig_ingr:
#                 raise ValueError("Ingrediente no encontrado")
#             if not meal.update_ingredient(ingredient_name, weight, orig_ingr):
#                 raise ValueError("Error al actualizar el ingrediente")
#             meal_model.meal_data = json.dumps(meal.to_json())
#             db.session.commit()
#             return meal
#         except Exception as e:
#             raise e

#     def add_ingredient(self, meal_id, query):
#         try:
#             meal_model = MealModel.query.get(meal_id)
#             if meal_model is None:
#                 raise ValueError("ID de comida no válido")
#             meal_data = json.loads(meal_model.meal_data)
#             meal = Meal.from_json(meal_data)
#             query_list = [f"{ingr.weight}g of {ingr.name}" for ingr in meal.ingredients]
#             query_list.append(query)
#             response = requests.post(Config.NUTRI_MACROS_API_URL, json={'query': query_list})
#             response.raise_for_status()
#             response_data = response.json()
#             if 'error' in response_data:
#                 raise ValueError(response_data['error'])
#             macros_dict = response_data
#             ingredients, cautions, diet_labels, health_labels = self.food_formatter.process_json(macros_dict)
#             meal.ingredients = ingredients
#             meal.cautions = cautions
#             meal.diet_labels = diet_labels
#             meal.health_labels = health_labels
#             meal_model.meal_data = json.dumps(meal.to_json())
#             db.session.commit()
#             return meal
#         except Exception as e:
#             raise e

#     def remove_ingredient(self, meal_id, ingredient_name):
#         try:
#             meal_model = MealModel.query.get(meal_id)
#             if meal_model is None:
#                 raise ValueError("ID de comida no válido")
#             meal_data = json.loads(meal_model.meal_data)
#             meal = Meal.from_json(meal_data)
#             if not meal.remove_ingredient_by_name(ingredient_name):
#                 raise ValueError("Ingrediente no encontrado")
#             query_list = [f"{ingr.weight}g of {ingr.name}" for ingr in meal.ingredients]
#             response = requests.post(Config.NUTRI_MACROS_API_URL, json={'query': query_list})
#             response.raise_for_status()
#             response_data = response.json()
#             if 'error' in response_data:
#                 raise ValueError(response_data['error'])
#             macros_dict = response_data
#             ingredients, cautions, diet_labels, health_labels = self.food_formatter.process_json(macros_dict)
#             meal.ingredients = ingredients
#             meal.cautions = cautions
#             meal.diet_labels = diet_labels
#             meal.health_labels = health_labels
#             meal_model.meal_data = json.dumps(meal.to_json())
#             db.session.commit()
#             return meal
#         except Exception as e:
#             raise e