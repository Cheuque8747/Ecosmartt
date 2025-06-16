from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
import json
import io
import csv

from database import get_db, Sensor, Lectura, Clima, Parcela, User, Alerta
from config import templates
from services.auth_service import get_current_active_user

router = APIRouter(prefix="/graficos", tags=["Graficos"])

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_graficos(
    request: Request,
    parcela_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Dashboard principal de gráficos con múltiples visualizaciones"""
    
    # Convertir cadena vacía a None
    if parcela_id == "":
        parcela_id = None
    else:
        parcela_id = int(parcela_id) if parcela_id else None
    
    # Gestión de permisos según rol
    if current_user.role == "agricultor":
        if not current_user.parcela_id:
            raise HTTPException(status_code=403, detail="No tienes una parcela asignada")
        parcela_id = current_user.parcela_id
        parcelas = [db.query(Parcela).get(parcela_id)]
    else:
        parcelas = db.query(Parcela).all()
        if not parcela_id and parcelas:
            parcela_id = parcelas[0].id
    
    # Obtener datos para los gráficos
    datos_graficos = {}
    
    if parcela_id:
        # 1. Datos de sensores por tipo (últimas 24 horas)
        fecha_limite = datetime.now() - timedelta(hours=24)
        sensores_parcela = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
        
        datos_sensores = {}
        for sensor in sensores_parcela:
            lecturas = db.query(Lectura).filter(
                Lectura.sensor_id == sensor.id,
                Lectura.timestamp >= fecha_limite
            ).order_by(Lectura.timestamp).all()
            
            if lecturas:
                datos_sensores[sensor.tipo] = {
                    'labels': [l.timestamp.strftime('%H:%M') for l in lecturas],
                    'data': [l.valor for l in lecturas],
                    'sensor_id': sensor.id
                }
        
        datos_graficos['sensores'] = datos_sensores
        
        # 2. Datos climáticos (últimos 7 días)
        clima_limite = datetime.now() - timedelta(days=7)
        datos_clima = db.query(Clima).filter(
            Clima.parcela_id == parcela_id,
            Clima.timestamp >= clima_limite
        ).order_by(Clima.timestamp).all()
        
        if datos_clima:
            datos_graficos['clima'] = {
                'labels': [c.timestamp.strftime('%d/%m %H:%M') for c in datos_clima],
                'temperatura': [c.temperatura for c in datos_clima],
                'humedad': [c.humedad for c in datos_clima],
                'presion': [c.presion for c in datos_clima],
                'viento': [c.viento for c in datos_clima]
            }
        
        # 3. Estadísticas de sensores
        estadisticas = {}
        for sensor in sensores_parcela:
            stats = db.query(
                func.min(Lectura.valor).label('min'),
                func.max(Lectura.valor).label('max'),
                func.avg(Lectura.valor).label('avg'),
                func.count(Lectura.valor).label('count')
            ).filter(Lectura.sensor_id == sensor.id).first()
            
            if stats and stats.count > 0:
                estadisticas[sensor.tipo] = {
                    'min': round(stats.min, 2) if stats.min else 0,
                    'max': round(stats.max, 2) if stats.max else 0,
                    'avg': round(stats.avg, 2) if stats.avg else 0,
                    'count': stats.count
                }
        
        datos_graficos['estadisticas'] = estadisticas
        
        # 4. Comparación de parcelas (solo para técnicos y agrónomos)
        if current_user.role != "agricultor":
            comparacion = []
            todas_parcelas = db.query(Parcela).all()
            for p in todas_parcelas:
                sensores_count = db.query(Sensor).filter(Sensor.parcela_id == p.id).count()
                lecturas_count = db.query(Lectura).join(Sensor).filter(
                    Sensor.parcela_id == p.id
                ).count()
                
                comparacion.append({
                    'nombre': p.nombre,
                    'sensores': sensores_count,
                    'lecturas': lecturas_count
                })
            
            datos_graficos['comparacion_parcelas'] = comparacion
        
        # 5. Distribución de tipos de sensores
        distribucion = db.query(
            Sensor.tipo,
            func.count(Sensor.id).label('cantidad')
        ).filter(Sensor.parcela_id == parcela_id).group_by(Sensor.tipo).all()
        
        datos_graficos['distribucion_sensores'] = {
            'labels': [d.tipo for d in distribucion],
            'data': [d.cantidad for d in distribucion]
        }
        
        # 6. Alertas recientes (últimos 7 días)
        alertas_limite = datetime.now() - timedelta(days=7)
        alertas_recientes = db.query(
            Alerta.tipo,
            func.count(Alerta.id).label('cantidad')
        ).filter(
            Alerta.id_parcela == parcela_id,
            Alerta.timestamp >= alertas_limite
        ).group_by(Alerta.tipo).all()
        
        datos_graficos['alertas_recientes'] = {
            'labels': [a.tipo for a in alertas_recientes],
            'data': [a.cantidad for a in alertas_recientes]
        }
    
    return templates.TemplateResponse(
        "graficos_dashboard.html",
        {
            "request": request,
            "user": current_user,
            "parcelas": parcelas,
            "parcela_id": parcela_id,
            "datos_graficos": json.dumps(datos_graficos)
        }
    )

@router.get("/sensor/{sensor_id}", response_class=HTMLResponse)
async def grafico_sensor_detalle(
    request: Request,
    sensor_id: str,
    dias: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Gráfico detallado de un sensor específico"""
    
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Verificar permisos
    if current_user.role == "agricultor" and sensor.parcela_id != current_user.parcela_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este sensor")
    
    # Obtener lecturas
    fecha_limite = datetime.now() - timedelta(days=dias)
    lecturas = db.query(Lectura).filter(
        Lectura.sensor_id == sensor_id,
        Lectura.timestamp >= fecha_limite
    ).order_by(Lectura.timestamp).all()
    
    # Preparar datos para el gráfico
    datos = {
        'labels': [l.timestamp.strftime('%d/%m %H:%M') for l in lecturas],
        'valores': [l.valor for l in lecturas],
        'sensor': {
            'id': sensor.id,
            'tipo': sensor.tipo,
            'ubicacion': sensor.ubicacion,
            'estado': sensor.estado
        }
    }
    
    # Calcular estadísticas adicionales
    if lecturas:
        valores = [l.valor for l in lecturas]
        datos['estadisticas'] = {
            'min': round(min(valores), 2),
            'max': round(max(valores), 2),
            'promedio': round(sum(valores) / len(valores), 2),
            'total_lecturas': len(valores)
        }
    
    return templates.TemplateResponse(
        "grafico_sensor.html",
        {
            "request": request,
            "user": current_user,
            "datos": json.dumps(datos),
            "sensor": sensor,
            "dias": dias
        }
    )

@router.get("/comparativo", response_class=HTMLResponse)
async def graficos_comparativos(
    request: Request,
    tipo_sensor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Gráficos comparativos entre sensores del mismo tipo"""
    
    if current_user.role == "agricultor":
        raise HTTPException(status_code=403, detail="No tienes permisos para ver comparativas")
    
    # Obtener tipos de sensores disponibles
    tipos_disponibles = db.query(Sensor.tipo).distinct().all()
    tipos_disponibles = [t[0] for t in tipos_disponibles]
    
    datos_comparativo = {}
    
    if tipo_sensor:
        # Obtener todos los sensores del tipo seleccionado
        sensores = db.query(Sensor).filter(Sensor.tipo == tipo_sensor).all()
        
        fecha_limite = datetime.now() - timedelta(hours=24)
        
        for sensor in sensores:
            lecturas = db.query(Lectura).filter(
                Lectura.sensor_id == sensor.id,
                Lectura.timestamp >= fecha_limite
            ).order_by(Lectura.timestamp).all()
            
            if lecturas:
                # Obtener nombre de la parcela
                parcela = db.query(Parcela).filter(Parcela.id == sensor.parcela_id).first()
                nombre_completo = f"{parcela.nombre if parcela else 'Sin parcela'} - {sensor.ubicacion}"
                
                datos_comparativo[nombre_completo] = {
                    'labels': [l.timestamp.strftime('%H:%M') for l in lecturas[-20:]],  # Últimas 20 lecturas
                    'data': [l.valor for l in lecturas[-20:]],
                    'sensor_id': sensor.id,
                    'estado': sensor.estado
                }
    
    return templates.TemplateResponse(
        "graficos_comparativos.html",
        {
            "request": request,
            "user": current_user,
            "tipos_disponibles": tipos_disponibles,
            "tipo_seleccionado": tipo_sensor,
            "datos_comparativo": json.dumps(datos_comparativo)
        }
    )

@router.get("/tendencias", response_class=HTMLResponse)
async def graficos_tendencias(
    request: Request,
    parcela_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Análisis de tendencias a largo plazo"""
    
    # Gestión de permisos
    if current_user.role == "agricultor":
        if not current_user.parcela_id:
            raise HTTPException(status_code=403, detail="No tienes una parcela asignada")
        parcela_id = current_user.parcela_id
        parcelas = [db.query(Parcela).get(parcela_id)]
    else:
        parcelas = db.query(Parcela).all()
        if not parcela_id and parcelas:
            parcela_id = parcelas[0].id
    
    tendencias = {}
    
    if parcela_id:
        # Análisis mensual de los últimos 6 meses
        fecha_inicio = datetime.now() - timedelta(days=180)
        
        sensores = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
        
        for sensor in sensores:
            # Agrupar por mes
            lecturas_mensuales = db.query(
                func.strftime('%Y-%m', Lectura.timestamp).label('mes'),
                func.avg(Lectura.valor).label('promedio'),
                func.min(Lectura.valor).label('minimo'),
                func.max(Lectura.valor).label('maximo')
            ).filter(
                Lectura.sensor_id == sensor.id,
                Lectura.timestamp >= fecha_inicio
            ).group_by('mes').order_by('mes').all()
            
            if lecturas_mensuales:
                tendencias[sensor.tipo] = {
                    'meses': [l.mes for l in lecturas_mensuales],
                    'promedios': [round(l.promedio, 2) for l in lecturas_mensuales],
                    'minimos': [round(l.minimo, 2) for l in lecturas_mensuales],
                    'maximos': [round(l.maximo, 2) for l in lecturas_mensuales]
                }
    
    return templates.TemplateResponse(
        "graficos_tendencias.html",
        {
            "request": request,
            "user": current_user,
            "parcelas": parcelas,
            "parcela_id": parcela_id,
            "tendencias": json.dumps(tendencias)
        }
    )

@router.get("/export/{tipo}", response_class=StreamingResponse)
async def exportar_datos_grafico(
    tipo: str,
    parcela_id: int = Query(...),
    formato: str = Query("csv", regex="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Exportar datos de gráficos en CSV o JSON"""
    
    # Verificar permisos
    if current_user.role == "agricultor" and parcela_id != current_user.parcela_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para exportar estos datos")
    
    # Obtener datos según el tipo
    if tipo == "sensores":
        fecha_limite = datetime.now() - timedelta(hours=24)
        sensores = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
        
        datos = []
        for sensor in sensores:
            lecturas = db.query(Lectura).filter(
                Lectura.sensor_id == sensor.id,
                Lectura.timestamp >= fecha_limite
            ).order_by(Lectura.timestamp).all()
            
            for lectura in lecturas:
                datos.append({
                    'sensor_id': sensor.id,
                    'tipo': sensor.tipo,
                    'ubicacion': sensor.ubicacion,
                    'timestamp': lectura.timestamp.isoformat(),
                    'valor': lectura.valor,
                    'unidad': lectura.unidad
                })
    
    elif tipo == "clima":
        fecha_limite = datetime.now() - timedelta(days=7)
        datos_clima = db.query(Clima).filter(
            Clima.parcela_id == parcela_id,
            Clima.timestamp >= fecha_limite
        ).order_by(Clima.timestamp).all()
        
        datos = [{
            'timestamp': c.timestamp.isoformat(),
            'temperatura': c.temperatura,
            'humedad': c.humedad,
            'presion': c.presion,
            'viento': c.viento,
            'descripcion': c.descripcion,
            'ubicacion': c.ubicacion
        } for c in datos_clima]
    
    else:
        raise HTTPException(status_code=400, detail="Tipo de exportación no válido")
    
    # Exportar según formato
    if formato == "json":
        output = io.StringIO()
        json.dump(datos, output, indent=2)
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=datos_{tipo}_{datetime.now().strftime('%Y%m%d')}.json"
            }
        )
    
    else:  # CSV
        output = io.StringIO()
        if datos:
            writer = csv.DictWriter(output, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=datos_{tipo}_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )