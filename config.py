import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NUTRI_API_URL = os.getenv('NUTRI_API_URL','http://127.0.0.1:5000/detect_food')  # URL para procesar imágenes
    NUTRI_MACROS_API_URL = os.getenv('NUTRI_MACROS_API_URL')  # URL para macros de EDAMAM
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meals.db'  # Base de datos SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RDA_FILE_PATH = os.getenv('RDA_FILE_PATH', 'config/default_rda.json')  # Ruta al archivo RDA