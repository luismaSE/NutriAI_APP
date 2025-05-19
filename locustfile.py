import json
import os
from locust import HttpUser, task, between
import uuid
import logging

# Configuración de logging para depuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutriAIUser(HttpUser):
    """
    Clase que simula un usuario de NutriAI realizando el camino típico de ejecución.
    Cada usuario realiza las tareas de registro, autenticación, carga de imagen y consulta de macros.
    """
    # Tiempo de espera entre tareas (1 a 5 segundos) para simular comportamiento realista
    wait_time = between(1, 5)

    def on_start(self):
        """
        Método que se ejecuta al iniciar cada usuario virtual.
        Realiza el registro y autenticación para obtener el JWT.
        """
        # Generar un nombre de usuario único
        self.username = f"user_{uuid.uuid4().hex[:8]}"
        self.password = "testpassword123"
        self.jwt_token = None

        # Registrar el usuario
        self.register_user()
        # Obtener el JWT
        self.login()

    def register_user(self):
        """
        Registra un nuevo usuario en el endpoint /register.
        Envía una solicitud POST con username y password.
        """
        try:
            response = self.client.post(
                "/register",
                json={"username": self.username, "password": self.password},
                name="Register User"
            )
            if response.status_code == 201:
                logger.info(f"Usuario {self.username} registrado correctamente")
            else:
                logger.error(f"Error al registrar usuario {self.username}: {response.text}")
        except Exception as e:
            logger.error(f"Excepción al registrar usuario {self.username}: {str(e)}")

    def login(self):
        """
        Autentica al usuario y obtiene el JWT desde el endpoint /login.
        """
        try:
            response = self.client.post(
                "/login",
                json={"username": self.username, "password": self.password},
                name="Login"
            )
            if response.status_code == 200:
                self.jwt_token = response.json().get("access_token")
                logger.info(f"JWT obtenido para {self.username}")
            else:
                logger.error(f"Error al autenticar usuario {self.username}: {response.text}")
        except Exception as e:
            logger.error(f"Excepción al autenticar usuario {self.username}: {str(e)}")

    @task
    def typical_execution_path(self):
        """
        Simula el camino típico de ejecución:
        1. Carga una imagen al endpoint /api/image.
        2. Construye una lista de queries con '1 serving of <ingredient>' desde la respuesta.
        3. Consulta el endpoint /get_macros con la lista de queries.
        """
        # Ruta de la imagen local (ajusta según tu entorno)
        image_path = "/home/luisma_se/Imágenes/burger.jpg"  # Asegúrate de tener una imagen en esta ruta

        if not os.path.exists(image_path):
            logger.error(f"Imagen no encontrada en {image_path}")
            return

        # Cargar la imagen al endpoint /api/image
        try:
            with open(image_path, "rb") as image_file:
                files = {"image": (os.path.basename(image_path), image_file, "image/jpeg")}
                headers = {"Authorization": f"Bearer {self.jwt_token}"}
                response = self.client.post(
                    "/api/image",
                    files=files,
                    headers=headers,
                    name="Upload Image"
                )

            if response.status_code == 200:
                response_data = response.json()
                detected_foods = response_data.get("detected_foods", [])

                if detected_foods:
                    # Construir una lista de queries en el formato '1 serving of <ingredient>'
                    query_list = [f"1 serving of {ingredient}" for ingredient in detected_foods]
                    logger.info(f"Queries generadas: {query_list}")

                    # Consultar el endpoint /get_macros con la lista de queries
                    response = self.client.post(
                        "/get_macros",
                        json={"query": query_list},
                        headers=headers,
                        name="Get Macros"
                    )

                    if response.status_code == 200:
                        logger.info(f"Macros obtenidos para {query_list}")
                    else:
                        logger.error(f"Error al obtener macros para {query_list}: {response.text}")
                else:
                    logger.warning("No se encontraron alimentos en la respuesta de /api/image")
            else:
                logger.error(f"Error al cargar imagen: {response.text}")
        except Exception as e:
            logger.error(f"Excepción al procesar imagen o macros: {str(e)}")

# Configuración para simular 20 usuarios concurrentes
host = "http://localhost:5005"  # Ajusta según la URL de tu NutriAI_APP