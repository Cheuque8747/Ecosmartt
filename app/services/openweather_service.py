import os
import requests
from database import Clima
from sqlalchemy.orm import Session

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

def guardar_clima(db: Session, data: dict, ubicacion: str):
    clima = Clima(
        temperatura=data["main"]["temp"],
        humedad=data["main"]["humidity"],
        presion=data["main"]["pressure"],
        viento=data["wind"]["speed"],
        descripcion=data["weather"][0]["description"],
        icono=data["weather"][0]["icon"],
        ubicacion=ubicacion
    )
    db.add(clima)
    db.commit()
    db.refresh(clima)
    return clima