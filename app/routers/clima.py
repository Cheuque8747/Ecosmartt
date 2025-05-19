from fastapi import APIRouter, Query, Request
from services.openweather_service import OpenWeatherService, guardar_clima
from config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import Clima, get_db
from fastapi import Depends

from services.auth_service import get_current_active_user
from database import User

router = APIRouter(prefix="/clima", tags=["Clima"])
weather_service = OpenWeatherService()

from typing import Optional
from fastapi import HTTPException
from database import Parcela

@router.get("/vista", response_class=HTMLResponse)
async def vista_clima(
    request: Request,
    parcela_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Muestra el clima actual y el pronóstico según el rol del usuario"""
    parcela = None
    ciudad = None

    if current_user.role == "agricultor":
        # Solo mostrar el clima de la parcela del agricultor
        if not current_user.parcela_id:
            raise HTTPException(status_code=403, detail="No tienes una parcela asignada")
        parcela_id = current_user.parcela_id
        parcela = db.query(Parcela).get(parcela_id)
        if not parcela:
            raise HTTPException(status_code=404, detail="Parcela no encontrada")
    else:
        # Técnicos y agrónomos pueden seleccionar parcelas
        parcelas = db.query(Parcela).all()
        if parcela_id:
            parcela = db.query(Parcela).get(parcela_id)
            if not parcela:
                raise HTTPException(status_code=404, detail="Parcela no encontrada")

    # Obtener el clima actual
    clima_actual = None
    if parcela:
        ciudad = parcela.ubicacion
        clima_actual = weather_service.get_current_weather(ciudad)

    # Obtener el pronóstico
    pronostico = None
    if parcela:
        pronostico = weather_service.get_forecast(parcela.ubicacion)

    """
    if parcela:
        print(f"Parcela seleccionada: {parcela.id}, Ubicación: {parcela.ubicacion}")
        print(f"Clima actual encontrado: {clima_actual}")
    """
    return templates.TemplateResponse(
        "clima.html",
        {
            "request": request,
            "user": current_user,
            "clima_actual": clima_actual,
            "pronostico": pronostico,
            "parcelas": parcelas if current_user.role != "agricultor" else None,
            "parcela_id": parcela_id,
            "parcela_nombre": parcela.nombre if parcela else None,
            "ciudad": ciudad
        }
    )


from datetime import datetime, timedelta
@router.get("/actual")
def clima_actual(
    ciudad: str = Query(..., description="Nombre de la ciudad"),
    db: Session = Depends(get_db)
):
    # Obtener el clima actual desde la API
    data = weather_service.get_current_weather(ciudad)
    # Guardar siempre el clima actual en la base de datos
    guardar_clima(db, data, ciudad)
    return data

@router.get("/pronostico")
def clima_pronostico(ciudad: str = Query(..., description="Nombre de la ciudad")):
    return weather_service.get_forecast(ciudad)


@router.get("/historial", response_class=HTMLResponse)
def historial_clima(
    request: Request,
    parcela_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Muestra el historial de clima según el rol del usuario"""
    if current_user.role == "agricultor":
        # Solo mostrar el historial de la parcela del agricultor
        if not current_user.parcela_id:
            raise HTTPException(status_code=403, detail="No tienes una parcela asignada")
        parcela_id = current_user.parcela_id
        parcela = db.query(Parcela).get(parcela_id)
        if not parcela:
            raise HTTPException(status_code=404, detail="Parcela no encontrada")
        historial = db.query(Clima).filter(Clima.parcela_id == parcela_id).order_by(Clima.timestamp.desc()).all()
        parcelas = [parcela]
    else:
        # Técnicos y agrónomos pueden seleccionar parcelas
        parcelas = db.query(Parcela).all()
        if parcela_id:
            historial = db.query(Clima).filter(Clima.parcela_id == parcela_id).order_by(Clima.timestamp.desc()).all()
        else:
            historial = db.query(Clima).order_by(Clima.timestamp.desc()).all()

    return templates.TemplateResponse(
        "clima_historial.html",
        {
            "request": request,
            "user": current_user,
            "historial": historial,
            "parcelas": parcelas,
            "parcela_id": parcela_id
        }
    )



