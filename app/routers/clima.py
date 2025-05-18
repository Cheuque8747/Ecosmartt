from fastapi import APIRouter, Query, Request
from services.openweather_service import OpenWeatherService, guardar_clima
from config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import Clima, get_db
from fastapi import Depends

router = APIRouter(prefix="/clima", tags=["Clima"])
weather_service = OpenWeatherService()


@router.get("/vista", response_class=HTMLResponse)
async def vista_clima(request: Request):
    return templates.TemplateResponse("clima.html", {"request": request})


from datetime import datetime, timedelta
@router.get("/actual")
def clima_actual(
    ciudad: str = Query(..., description="Nombre de la ciudad"),
    db: Session = Depends(get_db)
):
    data = weather_service.get_current_weather(ciudad)
    # Buscar el último registro de clima para la ciudad
    ultimo = db.query(Clima).filter(Clima.ubicacion == ciudad).order_by(Clima.timestamp.desc()).first()
    ahora = datetime.now()
    if not ultimo or (ahora - ultimo.timestamp) > timedelta(hours=1):
        guardar_clima(db, data, ciudad)
    return data

@router.get("/pronostico")
def clima_pronostico(ciudad: str = Query(..., description="Nombre de la ciudad")):
    return weather_service.get_forecast(ciudad)


@router.get("/historial", response_class=HTMLResponse)
def historial_clima(request: Request, db: Session = Depends(get_db)):
    historial = db.query(Clima).order_by(Clima.timestamp.desc()).limit(50).all()
    return templates.TemplateResponse("clima_historial.html", {"request": request, "historial": historial})