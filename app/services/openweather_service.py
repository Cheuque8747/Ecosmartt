import os
import requests
from database import Clima
from sqlalchemy.orm import Session
from database import Parcela

class OpenWeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        if not self.api_key:
            raise ValueError("Falta la variable OPENWEATHERMAP_API_KEY en el entorno")

    def get_current_weather(self, city: str, lang: str = "es", units: str = "metric"):
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "lang": lang,
            "units": units
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast(self, city: str, lang: str = "es", units: str = "metric"):
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "lang": lang,
            "units": units
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_current_weather_by_coords(self, lat: float, lon: float):
        """Obtiene el clima actual usando coordenadas."""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "lang": "es"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast_by_coords(self, lat: float, lon: float):
        """Obtiene el pronóstico usando coordenadas."""
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "lang": "es"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

def guardar_clima(db: Session, data: dict, nombre_ubicacion: str, parcela_id: int = None):
    """
    Guarda los datos del clima en la base de datos.
    
    Args:
        db: Sesión de base de datos
        data: Datos del clima de OpenWeather
        nombre_ubicacion: Nombre de la ubicación (ciudad/lugar)
        parcela_id: ID de la parcela (opcional)
    """
    # Si se proporciona parcela_id, verificar que existe
    if parcela_id:
        parcela = db.query(Parcela).filter(Parcela.id == parcela_id).first()
        if not parcela:
            print(f"Error: No se encontró una parcela con ID: {parcela_id}")
            raise ValueError(f"No se encontró una parcela con ID: {parcela_id}")
    else:
        # Si no se proporciona parcela_id, buscar por nombre_ubicacion
        parcela = db.query(Parcela).filter(Parcela.nombre_ubicacion == nombre_ubicacion).first()
        if parcela:
            parcela_id = parcela.id
        else:
            print(f"Advertencia: No se encontró una parcela con nombre_ubicacion: {nombre_ubicacion}")
            # Si no se encuentra, guardar sin parcela_id
            parcela_id = None

    clima = Clima(
        temperatura=data["main"]["temp"],
        humedad=data["main"]["humidity"],
        presion=data["main"]["pressure"],
        viento=data["wind"]["speed"],
        descripcion=data["weather"][0]["description"],
        icono=data["weather"][0]["icon"],
        ubicacion=nombre_ubicacion,  # Guardamos el nombre de la ubicación
        parcela_id=parcela_id
    )
    
    db.add(clima)
    db.commit()
    db.refresh(clima)
    
    print(f"Clima guardado exitosamente para {nombre_ubicacion}")
    return clima