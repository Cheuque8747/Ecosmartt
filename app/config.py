import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



# Definir la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR  # Directorio de la aplicación

# Crear directorios necesarios
os.makedirs(APP_DIR / "templates", exist_ok=True)
os.makedirs(APP_DIR / "static", exist_ok=True)
os.makedirs(BASE_DIR.parent / "data", exist_ok=True)  # data está en la raíz del proyecto


# Configuración de plantillas
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

# Ruta para el archivo de sensores
SENSORS_FILE = BASE_DIR.parent / "data" / "sensores.json"

# Ruta para el historial de lecturas
READINGS_HISTORY_FILE = BASE_DIR.parent / "data" / "lecturas_historial.json"

sensor_info = {
    "temperatura": {"icon": "fas fa-thermometer-half", "unit": "°C", "color": "tipo-temperatura"},
    "luz": {"icon": "fas fa-sun", "unit": "lux", "color": "tipo-luz"},
    "ph": {"icon": "fas fa-flask", "unit": "pH", "color": "tipo-ph"},
    "conductividad": {"icon": "fas fa-bolt", "unit": "dS/m", "color": "tipo-conductividad"},
    "humedad": {"icon": "fas fa-tint", "unit": "%", "color": "tipo-humedad"}
}






