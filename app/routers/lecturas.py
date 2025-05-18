
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from datetime import datetime
import io
import csv
from sqlalchemy.orm import Session

from database import get_db, Sensor, Lectura
from services import sensor_service, lecturas_service
from config import templates, sensor_info
from services.auth_service import get_current_active_user

router = APIRouter(tags=["lecturas"])

@router.get("/lecturas/{sensor_id}", response_class=HTMLResponse,
    summary="Ver lecturas de un sensor",
    description="Muestra la página con las lecturas y estadísticas de un sensor específico.")
async def ver_lecturas(
    request: Request, 
    sensor_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Muestra la página de lecturas de un sensor específico"""
    # Verificamos que el sensor existe
    sensor = sensor_service.obtener_sensor_por_id(db, sensor_id)
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Cargamos las lecturas
    lecturas = lecturas_service.obtener_lecturas_sensor(db, sensor_id)
    
    # Calculamos estadísticas
    estadisticas = lecturas_service.obtener_estadisticas_sensor(db, sensor_id)
    
    # Convertimos las lecturas a formato compatible con el template
    lecturas_formateadas = []
    for lectura in lecturas:
        lecturas_formateadas.append({
            "valor": lectura.valor,
            "timestamp": lectura.timestamp.isoformat(),
            "unidad": lectura.unidad,
            "tipo": lectura.tipo
        })
    
    return templates.TemplateResponse(
        "lecturas.html", 
        {
            "request": request,
            "sensor": sensor,
            "sensor_info": sensor_info,
            "lecturas": lecturas_formateadas,
            "min_valor": estadisticas["min_valor"],
            "max_valor": estadisticas["max_valor"],
            "promedio_valor": estadisticas["promedio_valor"],
            "user": current_user
        }
    )

@router.get("/api/sensores/{sensor_id}/lecturas-json",
    summary="Obtener lecturas de un sensor en JSON",
    description="Devuelve las lecturas y estadísticas de un sensor en formato JSON. Requiere autenticación.")
async def get_sensor_lecturas_json(
    sensor_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Devuelve las lecturas de un sensor en formato JSON"""
    # Verificamos que el sensor existe
    sensor = sensor_service.obtener_sensor_por_id(db, sensor_id)
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Cargamos las lecturas
    lecturas = lecturas_service.obtener_lecturas_sensor(db, sensor_id)
    
    # Calculamos estadísticas
    estadisticas = lecturas_service.obtener_estadisticas_sensor(db, sensor_id)
    
    # Convertimos las lecturas a formato JSON
    lecturas_json = []
    for lectura in lecturas:
        lecturas_json.append({
            "valor": lectura.valor,
            "timestamp": lectura.timestamp.isoformat(),
            "unidad": lectura.unidad,
            "tipo": lectura.tipo
        })
    
    return {
        "lecturas": lecturas_json,
        "min_valor": estadisticas["min_valor"],
        "max_valor": estadisticas["max_valor"],
        "promedio_valor": estadisticas["promedio_valor"]
    }