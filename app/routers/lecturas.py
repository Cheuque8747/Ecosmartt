from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from datetime import datetime
import io
import csv
from sqlalchemy.orm import Session

from database import get_db, Sensor, Lectura
from services import sensor_service, lecturas_service
from config import templates, sensor_info
from services.auth_service import get_current_active_user


import plotly.graph_objects as go
from io import StringIO

router = APIRouter(tags=["lecturas"])

@router.get("/lecturas/{sensor_id}", response_class=HTMLResponse,
    summary="Ver lecturas de un sensor",
    description="Muestra la página con las lecturas y estadísticas de un sensor específico.")
async def ver_lecturas(
    request: Request, 
    sensor_id: str,
    page: int = Query(1, ge=1, description="Número de página"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Muestra la página de lecturas de un sensor específico con paginación"""
    # Verificamos que el sensor existe
    sensor = sensor_service.obtener_sensor_por_id(db, sensor_id)
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Cargamos las lecturas con paginación
    lecturas_paginadas = lecturas_service.obtener_lecturas_sensor_paginadas(db, sensor_id, page, per_page=10)
    
    # Calculamos estadísticas
    estadisticas = lecturas_service.obtener_estadisticas_sensor(db, sensor_id)

    # Para el gráfico, obtenemos las últimas 20 lecturas sin paginación
    lecturas_grafico = lecturas_service.obtener_lecturas_sensor(db, sensor_id, limit=20)
    
    # Extraer datos para el gráfico (invertir orden para que sea cronológico)
    lecturas_grafico_reversed = list(reversed(lecturas_grafico))
    labels = [lectura.timestamp.isoformat() for lectura in lecturas_grafico_reversed]
    data = [lectura.valor for lectura in lecturas_grafico_reversed]

    # Crear el gráfico con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels,
        y=data,
        mode='lines+markers',
        line=dict(color='rgb(75, 192, 192)'),
        marker=dict(size=8),
        name='Lecturas'
    ))
    fig.update_layout(
        title='Últimas 20 Lecturas del Sensor',
        xaxis_title='Fecha y Hora',
        yaxis_title='Valor',
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )

    # Renderizar el gráfico como HTML
    graph_html = fig.to_html(full_html=False)

    # Convertimos las lecturas paginadas a formato compatible con el template
    lecturas_formateadas = []
    for lectura in lecturas_paginadas["lecturas"]:
        lecturas_formateadas.append({
            "valor": lectura.valor,
            "timestamp": lectura.timestamp.isoformat(),
            "unidad": lectura.unidad,
            "tipo": lectura.tipo,
        })
    
    return templates.TemplateResponse(
        "lecturas.html", 
        {
            "request": request,
            "sensor": sensor,
            "sensor_info": sensor_info,
            "lecturas": lecturas_formateadas,
            "paginacion": lecturas_paginadas,
            "min_valor": estadisticas["min_valor"],
            "max_valor": estadisticas["max_valor"],
            "promedio_valor": estadisticas["promedio_valor"],
            "user": current_user,
            "graph_html": graph_html
        }
    )

@router.get("/api/sensores/{sensor_id}/lecturas-json",
    summary="Obtener lecturas de un sensor en JSON",
    description="Devuelve las lecturas y estadísticas de un sensor en formato JSON. Requiere autenticación.")
async def get_sensor_lecturas_json(
    sensor_id: str,
    page: int = Query(1, ge=1, description="Número de página"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Devuelve las lecturas de un sensor en formato JSON con paginación"""
    # Verificamos que el sensor existe
    sensor = sensor_service.obtener_sensor_por_id(db, sensor_id)
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Cargamos las lecturas con paginación
    lecturas_paginadas = lecturas_service.obtener_lecturas_sensor_paginadas(db, sensor_id, page, per_page=10)
    
    # Calculamos estadísticas
    estadisticas = lecturas_service.obtener_estadisticas_sensor(db, sensor_id)
    
    # Convertimos las lecturas a formato JSON
    lecturas_json = []
    for lectura in lecturas_paginadas["lecturas"]:
        lecturas_json.append({
            "valor": lectura.valor,
            "timestamp": lectura.timestamp.isoformat(),
            "unidad": lectura.unidad,
            "tipo": lectura.tipo
        })
    
    return {
        "lecturas": lecturas_json,
        "paginacion": {
            "page": lecturas_paginadas["page"],
            "per_page": lecturas_paginadas["per_page"],
            "total_lecturas": lecturas_paginadas["total_lecturas"],
            "total_pages": lecturas_paginadas["total_pages"],
            "has_prev": lecturas_paginadas["has_prev"],
            "has_next": lecturas_paginadas["has_next"]
        },
        "min_valor": estadisticas["min_valor"],
        "max_valor": estadisticas["max_valor"],
        "promedio_valor": estadisticas["promedio_valor"]
    }