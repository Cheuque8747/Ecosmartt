# 🌱 EcoSmart - Plataforma de Agricultura Inteligente

[![Estado del Proyecto](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow)](https://github.com/yourusername/ecosmart)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0+-brightgreen)](https://fastapi.tiangolo.com/)

## 📋 Descripción

EcoSmart es una plataforma integral para el monitoreo y gestión inteligente de cultivos agrícolas, que aprovecha tecnologías como Internet de las Cosas (IoT), inteligencia artificial y análisis avanzado de datos para optimizar la producción agrícola, haciéndola más eficiente, sostenible y resiliente.

El proyecto surge como respuesta a los desafíos actuales de la agricultura:
- Cambio climático que altera patrones tradicionales de cultivo
- Escasez de recursos hídricos en diversas regiones
- Creciente demanda de alimentos por el aumento poblacional
- Necesidad de reducir el impacto ambiental de prácticas agrícolas tradicionales

## 🚀 Características Principales

- 📊 *Simulador de Sensores Agrícolas:* Generación de datos realistas (temperatura, humedad, pH del suelo, etc.)
- 📱 *Panel de Control Intuitivo:* Visualización de información relevante de cultivos
- 🤖 *Asistente IA para Agricultura:* Integración con APIs de modelos ML (Deepseek)
- 🌦 *Integración Meteorológica:* Conexión con OpenWeatherMap para pronósticos
- ⚠ *Sistema de Alertas:* Notificaciones basadas en condiciones predefinidas

## 🛠 Tecnologías Utilizadas

- *Backend:* Python (FastAPI/Flask)
- *Frontend:* HTML/CSS con Bootstrap
- *IA:* APIs de Deepseek 
- *Simulación:* Python para simulación en tiempo real
- *Base de Datos:* SQLite para una implementación sencilla
- *APIs Externas:* OpenWeatherMap para datos meteorológicos

## 📁 Estructura del Proyecto

```plaintext
ecosmart/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Punto de inicio de FastAPI
│   ├── config.py                # Configuración general y rutas
│
│   ├── models/                  # Modelos de datos (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── sensor.py            # Modelo de sensor
│   │   └── user.py              # Modelo de usuario
│
│   ├── routers/                 # Rutas y endpoints principales
│   │   ├── __init__.py
│   │   ├── auth.py              # Autenticación y usuarios
│   │   ├── lecturas.py          # Lecturas de sensores
│   │   └── sensores.py          # Gestión de sensores
│
│   ├── services/                # Lógica de negocio y servicios externos
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Servicio de autenticación
│   │   ├── lecturas_service.py  # Servicio de lecturas
│   │   └── sensor_service.py    # Servicio de sensores
│
│   ├── static/                  # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   ├── imagenes/
│   │   └── js/
│
│   ├── templates/               # Plantillas HTML (Jinja2)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── lecturas.html
│   │   └── login.html
│
├── data/                        # Archivos de base de datos y datos persistentes
│   └── ecosmart.db
│
├── env/                         # Entorno virtual (no se sube a git)
│
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Explicación y documentación
```

- La integración con APIs externas como Deepseek y OpenWeatherMap se realiza desde los servicios en `app/services/`.
- La base de datos SQLite se encuentra en la carpeta `data/`.
- Los archivos estáticos y plantillas para el frontend están en `app/static/` y `app/templates/` respectivamente.
- El entorno virtual debe estar en la carpeta `env/` y está excluido en `.gitignore`.

## ⚙ Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- Git
- Acceso a APIs (OpenWeatherMap y Deepseek)

### Pasos de Instalación

1. *Clonar el repositorio*
   bash
   git clone https://github.com/cheuque1/ecosmart.git
   cd ecosmart
   

2. *Crear y activar entorno virtual*
   bash
   # En Windows
   python -m venv venv
   venv\Scripts\activate

   # En MacOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   

3. *Instalar dependencias*
   bash
   pip install -r requirements.txt
   

4. *Configurar variables de entorno*
   - Crear archivo .env en la raíz del proyecto
   
   OPENWEATHERMAP_API_KEY=tu_clave_api
   DEEPSEEK_API_KEY=tu_clave_api
   OLLAMA_API_URL=url_del_servicio
   

5. *Iniciar la aplicación*
   bash
   python run.py
   
   La aplicación estará disponible en http://localhost:8000

## 🖥 Uso

### Acceso al Panel de Control
1. Acceder a http://localhost:8000 desde cualquier navegador
2. Iniciar sesión con las credenciales proporcionadas (usuario: admin, contraseña: ecosmart)

### Funcionalidades principales
- *Dashboard*: Visualización general de todos los sensores y métricas
- *Monitoreo de Parcelas*: Datos en tiempo real de cada zona de cultivo
- *Asistente IA*: Consultas sobre estado de cultivos, enfermedades, optimización
- *Pronóstico Meteorológico*: Datos climáticos para planificación agrícola
- *Alertas*: Configuración de umbrales para notificaciones automáticas

## 👥 Usuarios del Sistema

- *Agricultores*: Monitoreo de cultivos, recepción de alertas y recomendaciones
- *Agrónomos*: Análisis detallado de datos, consultas específicas al asistente IA
- *Técnicos*: Configuración del sistema, ajuste de parámetros, mantenimiento

## 📝 Casos de Uso del Asistente IA

1. *Diagnóstico de Enfermedades*:
   
   Usuario: "La planta tiene manchas amarillas en las hojas y pequeños insectos debajo"
   IA: Análisis del problema, identificación de posible plaga y recomendaciones de tratamiento
   

2. *Optimización de Riego*:
   
   Sistema: Envía datos de humedad del suelo, tipo de cultivo y previsión meteorológica
   IA: Sugiere frecuencia e intensidad de riego óptimas, considerando todos los factores
   

3. *Planificación de Cultivos*:
   
   Usuario: "¿Qué cultivos son adecuados para sembrar en esta región en octubre?"
   IA: Recomendaciones basadas en clima, tipo de suelo y condiciones locales

   
# 👨‍💻 Configuración del Entorno de Desarrollo

## 1. Requisitos Previos

### Software Necesario
- Python 3.9+ ([Descargar](https://www.python.org/downloads/))
- Git ([Descargar](https://git-scm.com/downloads))
- Editor de código (recomendado: VS Code, [Descargar](https://code.visualstudio.com/))
- SQLite Browser (opcional, para gestión visual de BD, [Descargar](https://sqlitebrowser.org/))

### Conocimientos Recomendados
- Python básico/intermedio
- Conocimientos básicos de API REST
- HTML/CSS básico
- Bootstrap 5
- Git y control de versiones

## 2. Configuración del Entorno Python

### Crear y Activar Entorno Virtual

bash
#### * Windows
python -m venv venv
venv\Scripts\activate

#### * Linux/MacOS
python3 -m venv venv
source venv/bin/activate

## 3. Configuración de Base de Datos SQLite

### Crear el Archivo de Base de Datos
La base de datos se creará automáticamente con SQLAlchemy, pero es recomendable definir el esquema de antemano.

Crear un archivo `app/database/db.py`:

## Configuración de SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL para una base de datos SQLite local
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecosmart.db"

# Para una base de datos en memoria durante el desarrollo:
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Crear el motor de la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crear una clase de sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear clase base para los modelos
Base = declarative_base()
```


# Función de dependencia para obtener la DB session
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
``` 
## 4. Configuración de Deepseek API

### Crear Archivo de Configuración
Crear archivo `.env` en la raíz del proyecto:


## Archivo de configuración `.env`

```bash
# Configuración general
DEBUG=True
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria

# APIs externas
DEEPSEEK_API_KEY=tu_clave_api_deepseek
OPENWEATHERMAP_API_KEY=tu_clave_api_openweathermap

# Configuración de correo (para alertas)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASSWORD=tu_contraseña_o_app_password
```
## 5. Configuración del Frontend

El proyecto EcoSmart utiliza HTML y CSS puro para la interfaz de usuario, con el soporte del framework **[Bootstrap 5](https://getbootstrap.com/)** para facilitar el diseño responsivo y componentes visuales listos para usar.

### Incluir Bootstrap en tus plantillas

Puedes incluir Bootstrap directamente desde el CDN oficial en tus archivos HTML:

```html
<!-- Bootstrap 5 desde CDN -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
```

Esto te permite usar todas las clases y componentes de Bootstrap sin necesidad de descargar nada localmente.

---

## 6. Configuración de Git y Control de Versiones

### Inicialización del Repositorio

```bash
git init
```

### Crear `.gitignore`

Crear un archivo `.gitignore` con las siguientes reglas para Python y entornos virtuales:

```plaintext
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Entorno virtual
venv/
ENV/

# Archivos de base de datos
*.db
*.sqlite3

# Entorno
.env

# Logs
*.log

# IDE específicos
.idea/
.vscode/
*.swp
*.swo

# OS específicos
.DS_Store
Thumbs.db
```
## 7. Servicio de Clima con OpenWeatherMap

Archivo: `app/services/openweather.py`

```python
import os, aiohttp, logging
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()
logger = logging.getLogger(__name__)

class OpenWeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            logger.error("API key no encontrada.")
            raise ValueError("Falta OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_current_weather(self, lat: float, lon: float, lang: str = "es") -> Dict[str, Any]:
        params = {
            "lat": lat, "lon": lon,
            "appid": self.api_key,
            "units": "metric", "lang": lang
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/weather", params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    logger.error(f"Error {resp.status}: {await resp.text()}")
        except Exception as e:
            logger.error(f"Excepción: {str(e)}")
            return {"error": str(e)}
```

---
## 📊 Planificación del Proyecto

El proyecto se desarrolla en 15 semanas, organizadas en tres hitos principales:

1. *HITO 1: DEFINICIÓN Y DISEÑO* (Semanas 1-5)
   - Análisis de requisitos
   - Exploración de APIs
   - Diseño de arquitectura
   - Diseño de interfaces
   - Configuración del entorno

2. *HITO 2: DESARROLLO BÁSICO* (Semanas 6-10)
   - Implementación del simulador
   - Desarrollo del backend
   - Integración con APIs externas
   - Desarrollo del frontend
   - Prototipo funcional integrado

3. *HITO 3: FUNCIONALIDADES AVANZADAS* (Semanas 11-15)
   - Sistema de consultas IA avanzado
   - Sistema de alertas y notificaciones
   - Visualizaciones avanzadas
   - Testing y optimización
   - Documentación final y presentación


## 👨‍💻 Equipo

El proyecto está desarrollado por un equipo de 4 estudiantes con los siguientes roles:
- Frontend Developer: Nicolás Valdivia y Joaquín Vicencio
- Backend Developer: Víctor Cheuque y Joaquín Moraga

## 📄 Licencia

N/D

## 📧 Contacto
- *Universidad de Talca* - Ingeniería Civil en Computación
