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
Ecosmartt/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Punto de inicio de FastAPI
│   ├── config.py                # Configuración general y rutas
│   ├── database.py              # Modelos y conexión a la base de datos
│   ├── routers/                 # Rutas y endpoints principales
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── ia.py
│   │   ├── lecturas.py
│   │   ├── parcelas.py
│   │   ├── sensores.py
│   │   ├── clima.py
│   │   ├── chat_ia.py
│   │   ├── umbrales.py
│   │   ├── alertas.py
│   │   └── graficos.py
│   ├── services/                # Lógica de negocio y servicios externos
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── deepseek_service.py
│   │   ├── openweather_service.py
│   │   └── sensor_service.py
│   ├── models/                  # Modelos Pydantic y de dominio
│   │   ├── __init__.py
│   │   ├── sensor.py
│   │   ├── chat_ia.py
│   │   └── chat_ia.py
│   ├── templates/               # Plantillas HTML (Jinja2)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── lecturas.html
│   │   ├── login.html
│   │   ├── parcelas.html
│   │   ├── parcelas_mapa.html
│   │   ├── perfil.html
│   │   ├── clima.html
│   │   ├── graficos_dashboard.html
│   │   ├── graficos_tendencias.html
│   │   ├── inicio.html
│   │   └── trabajadores_parcela.html
│   └── ...
├── data/                        # Archivos de base de datos y datos persistentes
│   └── ecosmart.db
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Documentación principal
└── .env                         # Variables de entorno (no subir a git)
```
- La base de datos SQLite se encuentra en la carpeta `data/`.
- Las vistas o plantillas para el frontend están en `app/templates/`.
- Los servicios externos y lógica de negocio están en `app/services/`.
- Los endpoints y rutas principales están en `app/routers/`.

## ⚙ Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- Git
- Acceso a APIs (OpenWeatherMap y Deepseek)

### Pasos de Instalación

1. *Clonar el repositorio*
   bash
   git clone https://github.com/Cheuque8747/Ecosmartt.git
   cd ecosmartt
   

2. *Crear y activar entorno virtual*
   
   # En Windows
   python -m venv env
   env\Scripts\activate

   # En MacOS/Linux
   python3 -m venv env
   source env/bin/activate
> **Nota:**  
> Si al intentar activar el entorno virtual en Windows (`env\Scripts\activate`) recibes un error relacionado con permisos de ejecución de scripts, puedes solucionarlo ejecutando el siguiente comando en PowerShell antes de activar el entorno:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
> Esto otorga permisos temporales solo para la sesión actual y permite activar el entorno virtual sin problemas de seguridad.
   

3. *Instalar dependencias*
   
     pip install -r requirements.txt
   

4. *Configurar variables de entorno*
   - Crear archivo .env en la raíz del proyecto
   
   OPENWEATHERMAP_API_KEY=tu_clave_api
   DEEPSEEK_API_KEY=tu_clave_api
   OLLAMA_API_URL=url_del_servicio
   


5. *Iniciar la aplicación*

   Para iniciar la aplicación (teniendo el entorno virtual activo), primero debes ubicarte dentro de la carpeta `app` desde la terminal. Luego ejecuta el siguiente comando:

   uvicorn main:app --reload

## 🖥 Uso

### Acceso a la aplicación
1. Acceder a http://127.0.0.1:8000/auth/login desde cualquier navegador
2. Iniciar sesión con las credenciales (usuario y contraseña) de un usuario de la base de datos

> **Nota:**  Si al iniciar la aplicación no tiene un base de datos, se crea una con un usuario genérico con rol de técnico con las credenciales
>
> usuario: "admin" y contraseña: "admin123"

### Funcionalidades principales
- *Dashboard*: Visualización general de todos los sensores y métricas
- *Mapa de Parcelas*: Visualización geográfica de las parcelas con sus sensores
- *Asistente IA*: Consultas sobre estado de cultivos, enfermedades, optimización
- *Pronóstico Meteorológico*: Datos climáticos para planificación agrícola
- *Alertas*: Configuración de umbrales para notificaciones automáticas

## 👥 Usuarios del Sistema

- *Agricultores*: Monitoreo de sensores, recepción de alertas y acceso limitado a datos de su parcela 
- *Agrónomos*: Análisis detallado de datos y acceso a datos de todas las parcelas
- *Técnicos*: Configuración del sistema, ajuste de parámetros, creación de parcelas y sensores, control total



## 📖 Guía de Uso por Rol

### 👨‍🌾 Agricultor

- **Monitoreo de Sensores y Clima:**  
  Accede a las opciones del navbar, tales como, sensores, clima actual, entre otros:  
  - Visualiza datos en tiempo real de temperatura, humedad, pH y luz solar.
  - Recibe alertas automáticas si algún valor supera los umbrales definidos.

- **Consultas al Asistente IA:**  
  Usa la sección "Asistente IA" para hacer preguntas sobre el estado de tus cultivos, diagnóstico de enfermedades o recomendaciones de riego.  
  - Elige una plantilla de consulta rápida (por ejemplo, "Diagnóstico de Enfermedades").
  - El sistema usará automáticamente los datos de tu parcela.

- **Historial y Alertas:**  
  Consulta el historial de alertas desde la opcion de alertas en el navabr.

---

### 👨‍🔬 Agrónomo

- **Visualización de Parcelas:**  
  Accede al dashboard para ver todas las parcelas bajo tu supervisión.  
  - Filtra por parcela usando el selector en la parte superior.
  - Analiza tendencias y comparativas entre parcelas.

- **Consultas al Asistente IA:**  
  Selecciona la parcela de interés en la barra lateral del asistente IA antes de usar una plantilla.  
  - Puedes consultar sobre riego, fertilización, plagas, clima y cosecha.
  - El asistente te mostrará recomendaciones basadas en los datos de la parcela seleccionada.

- **Gestión de Sensores y Lecturas:**  
  Visualiza y analiza las lecturas históricas de los sensores de cada parcela.
  - Descarga reportes o exporta datos si es necesario.

---

### 🛠 Técnico

- **Gestión de Usuarios y Parcelas:**  
  Desde el menú de "Parcelas" y "Trabajadores", crea, edita o elimina parcelas y usuarios asociados.
  - Asigna roles y parcelas a cada trabajador.
  - Usa los formularios modales para una gestión rápida.

- **Configuración de Umbrales:**  
  Accede a la sección de "Configuración" para definir los valores de alerta para cada tipo de sensor en cada parcela.
  - Ajusta los umbrales según las necesidades de cada zona.

- **Supervisión General:**  
  Visualiza el estado global del sistema, sensores activos, alertas recientes y estadísticas rápidas desde el dashboard.
  - Utiliza las visualizaciones avanzadas para detectar anomalías o necesidades de mantenimiento.

- **Soporte y Mantenimiento:**  
  Realiza pruebas, revisa logs y asegura el correcto funcionamiento de la plataforma.

---

> **Tip:**  
> Todas las funciones principales están accesibles desde el navbar. El sistema adapta las opciones visibles según tu rol.


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