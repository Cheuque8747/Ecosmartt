from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from typing import Optional, List
import io
import csv
from datetime import datetime
from sqlalchemy.orm import Session

from models.sensor import Sensor as SensorPydantic, SensorCreate
from database import get_db, Sensor
from services import sensor_service
from config import templates, sensor_info
from services.auth_service import get_current_active_user
from database import Parcela

router = APIRouter(tags=["sensores"])

# API Routes
@router.get(
    "/api/sensores",
    response_model=List[SensorPydantic],
    summary="Listar sensores",
    description="Obtiene la lista de sensores registrados en la plataforma. Permite filtrar por tipo, estado y ubicación. Requiere autenticación."
)
async def get_sensores(
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    ubicacion: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Devuelve una lista de sensores registrados en la plataforma.
    Permite filtrar por tipo, estado y ubicación.
    Requiere autenticación.
    """
    return sensor_service.filtrar_sensores(db, tipo, estado, ubicacion)

@router.get(
    "/api/sensores/{sensor_id}",
    #response_model=SensorPydantic,
    summary="Obtener sensor por ID",
    description="Obtiene la información detallada de un sensor específico por su ID. Requiere autenticación."
)
async def get_sensor(
    sensor_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Devuelve la información de un sensor específico por su ID.
    Requiere autenticación.
    """
    sensor = sensor_service.obtener_sensor_por_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Incluir la información de la parcela asociada
    parcela = sensor.parcela
    parcela_info = {
        "id": parcela.id,
        "nombre": parcela.nombre,
        "ubicacion": parcela.ubicacion
    } if parcela else None

    print(parcela_info["ubicacion"]   )
    return {
        "id": sensor.id,
        "tipo": sensor.tipo,
        "ubicacion": sensor.ubicacion,
        "frecuencia_lectura": sensor.frecuencia_lectura,
        "min_lectura": sensor.min_lectura,
        "max_lectura": sensor.max_lectura,
        "ruido": sensor.ruido,
        "estado": sensor.estado,
        "promedio": sensor.promedio,
        "parcela": parcela_info  # Agregar información de la parcela
    }

    return sensor

@router.post(
    "/api/sensores",
    response_model=SensorPydantic,
    summary="Crear sensor",
    description="Crea un nuevo sensor en la plataforma. Solo los usuarios con rol técnico pueden crear sensores. Requiere autenticación."
)
async def create_sensor(
    sensor: SensorCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Crea un nuevo sensor en la plataforma.
    Solo los usuarios con rol técnico pueden crear sensores.
    Requiere autenticación.
    """
    # Verificar que el usuario es técnico
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="Solo los técnicos pueden crear sensores")
    
    # Generamos un ID único para el sensor
    total_sensores = db.query(Sensor).count()
    new_id = str(total_sensores + 1).zfill(3)
    
    # Crear el sensor
    return sensor_service.crear_sensor(db, sensor, new_id)

@router.put(
    "/api/sensores/{sensor_id}",
    response_model=SensorPydantic,
    summary="Actualizar sensor",
    description="Actualiza los datos de un sensor existente. Solo los usuarios con rol técnico pueden actualizar sensores. Requiere autenticación."
)
async def update_sensor(
    sensor_id: str, 
    sensor_update: SensorCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Actualiza los datos de un sensor existente.
    Solo los usuarios con rol técnico pueden actualizar sensores.
    Requiere autenticación.
    """
    # Verificar que el usuario es técnico
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="Solo los técnicos pueden actualizar sensores")
    
    # Convertir a diccionario para actualizar
    sensor_data = sensor_update.dict()
    
    # Actualizar el sensor
    updated_sensor = sensor_service.actualizar_sensor(db, sensor_id, sensor_data)
    
    if not updated_sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    return updated_sensor

@router.delete(
    "/api/sensores/{sensor_id}",
    summary="Eliminar sensor",
    description="Elimina un sensor de la plataforma. Solo los usuarios con rol técnico pueden eliminar sensores. Requiere autenticación."
)
async def delete_sensor(
    sensor_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Elimina un sensor de la plataforma.
    Solo los usuarios con rol técnico pueden eliminar sensores.
    Requiere autenticación.
    """
    # Verificar que el usuario es técnico
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="Solo los técnicos pueden eliminar sensores")
    
    # Eliminar el sensor
    result = sensor_service.eliminar_sensor(db, sensor_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    return {"message": f"Sensor {sensor_id} eliminado correctamente"}

@router.put(
    "/api/sensores/{sensor_id}/toggle-estado",
    summary="Cambiar estado de sensor",
    description="Cambia el estado de un sensor entre activo y noActivo. Solo los usuarios con rol técnico pueden cambiar el estado. Requiere autenticación."
)
async def toggle_sensor_state(
    sensor_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Cambia el estado de un sensor entre activo y noActivo.
    Solo los usuarios con rol técnico pueden cambiar el estado.
    Requiere autenticación.
    """
    # Verificar que el usuario es técnico
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="Solo los técnicos pueden cambiar el estado de sensores")
    
    # Cambiar el estado del sensor
    updated_sensor = sensor_service.cambiar_estado_sensor(db, sensor_id)
    
    if not updated_sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    return {"message": f"Estado del sensor {sensor_id} cambiado a {updated_sensor.estado}"}

@router.get(
    "/api/sensores/{sensor_id}/lectura",
    summary="Obtener/generar última lectura de sensor",
    description="Obtiene la última lectura de un sensor o genera una nueva si corresponde. Requiere autenticación."
)
async def get_sensor_lectura(
    sensor_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene la última lectura de un sensor o genera una nueva si corresponde.
    Requiere autenticación.
    """
    from services.lecturas_service import generar_lectura, guardar_lectura
    from datetime import timedelta
    
    # Obtener el sensor
    sensor = sensor_service.obtener_sensor_por_id(db, sensor_id)
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Verificamos si el sensor está activo
    if (sensor.estado != "activo"):
        return {"error": "El sensor no está activo"}

    # Generar lectura
    lectura = generar_lectura(db, sensor, ignore_time_check=True)
    
    # Si se generó una nueva lectura, actualizamos la última medición
    if lectura is not None:
        timestamp = datetime.now()
        
        # Actualizar última medición del sensor
        sensor.ultima_medicion = timestamp
        db.commit()
        
        # Guardamos la lectura en la base de datos
        unidad = sensor_info[sensor.tipo]["unit"]
        guardar_lectura(db, sensor_id, lectura, timestamp, unidad, sensor.tipo)
        
        # Preparamos la respuesta con la información de la lectura
        return {
            "sensor_id": sensor_id,
            "tipo": sensor.tipo,
            "valor": lectura,
            "unidad": unidad,
            "timestamp": sensor.ultima_medicion
        }
    else:
        # Devolvemos info de que aún no es tiempo para una nueva lectura
        tiempo_espera = (sensor.ultima_medicion + 
                        timedelta(seconds=sensor.frecuencia_lectura) - 
                        datetime.now()).total_seconds()
        
        return {
            "mensaje": "Aún no es tiempo para una nueva lectura",
            "tiempo_espera_segundos": max(0, tiempo_espera),
            "ultima_lectura_timestamp": sensor.ultima_medicion
        }

@router.get(
    "/api/sensores/{sensor_id}/export",
    summary="Exportar lecturas de sensor a CSV",
    description="Exporta todas las lecturas de un sensor en formato CSV. Requiere autenticación."
)
async def export_sensor_readings(
    sensor_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Exporta todas las lecturas de un sensor en formato CSV.
    Requiere autenticación.
    """
    from services.lecturas_service import obtener_lecturas_sensor
    
    # Verificamos que el sensor existe
    sensor = sensor_service.obtener_sensor_por_id(db, sensor_id)
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Obtenemos las lecturas
    lecturas = obtener_lecturas_sensor(db, sensor_id)
    
    # Ordenamos por timestamp (ascendente)
    lecturas.sort(key=lambda x: x.timestamp)
    
    # Creamos un archivo CSV en memoria 
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')  # Usamos punto y coma como separador
    
    # Escribimos solo la cabecera de la tabla de lecturas
    writer.writerow(['NUMERO', 'FECHA', 'HORA', 'VALOR', 'UNIDAD'])
    
    # Escribimos los datos en filas y columnas
    for i, lectura in enumerate(lecturas, 1):
        timestamp = lectura.timestamp.isoformat().replace('T', ' ').split('.')[0]
        fecha = timestamp.split(' ')[0] if ' ' in timestamp else timestamp
        hora = timestamp.split(' ')[1] if ' ' in timestamp else ''
        
        # Aseguramos que el valor tenga 2 decimales
        valor = round(float(lectura.valor), 2)
        
        writer.writerow([
            i, 
            fecha, 
            hora, 
            valor, 
            lectura.unidad
        ])
    
    # Configuramos la respuesta
    output.seek(0)
    
    # Nombre de archivo simple
    fecha_actual = datetime.now().strftime('%Y%m%d')
    nombre_archivo = f"lecturas_sensor_{sensor.id}_{fecha_actual}.csv"
    
    headers = {
        'Content-Disposition': f'attachment; filename="{nombre_archivo}"'
    }
    
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers=headers
    )

# Rutas para el formulario
@router.post("/sensores/add")
async def add_sensor_form(
    request: Request,
    #se quito el campo sensorId ya que no es necesario al crear un nuevo sensor
    sensorTipo: str = Form(...),
    sensorUbicacion: str = Form(...),
    sensorFrecuencia: int = Form(...),
    sensorMinLectura: float = Form(...),
    sensorMaxLectura: float = Form(...),
    sensorRuido: Optional[float] = Form(0.0),
    sensorEstado: str = Form("activo"),
    sensorPromedio: float = Form(...),
    parcelaId: int = Form(...),  # Nuevo campo para la parcela
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Añade un nuevo sensor desde un formulario"""
    # Verificar que el usuario es técnico
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="Solo los técnicos pueden crear sensores")

    # Verificar que la parcela existe
    parcela = db.query(Parcela).get(parcelaId)
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela no encontrada")

    # Generar un ID único para el sensor
    total_sensores = db.query(Sensor).count()
    sensorId = str(total_sensores + 1).zfill(3)

    # Crear el sensor
    nuevo_sensor = SensorCreate(
        tipo=sensorTipo,
        frecuencia_lectura=sensorFrecuencia,
        max_lectura=sensorMaxLectura,
        min_lectura=sensorMinLectura,
        ruido=sensorRuido,
        ubicacion=sensorUbicacion,
        estado=sensorEstado,
        promedio=sensorPromedio
    )
    sensor_service.crear_sensor(db, nuevo_sensor, sensorId, parcelaId)

    # CORREGIDO: Redirigir a /sensores en lugar de /
    return RedirectResponse("/sensores", status_code=303)

@router.post("/sensores/edit")
async def edit_sensor_form(
    request: Request,
    sensorId: str = Form(...),
    sensorTipo: str = Form(...),
    sensorUbicacion: str = Form(...),
    sensorFrecuencia: int = Form(...),
    sensorMinLectura: float = Form(...),
    sensorMaxLectura: float = Form(...),
    sensorRuido: Optional[float] = Form(0.0),
    sensorEstado: str = Form("activo"),
    sensorPromedio: float = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Actualiza un sensor existente desde un formulario"""
    # Verificar que el usuario es técnico
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="Solo los técnicos pueden editar sensores")
    
    # Verificamos si el sensor existe
    sensor_existente = sensor_service.obtener_sensor_por_id(db, sensorId)
    
    if not sensor_existente:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    # Datos para actualizar
    sensor_data = {
        "tipo": sensorTipo,
        "frecuencia_lectura": sensorFrecuencia,
        "max_lectura": sensorMaxLectura,
        "min_lectura": sensorMinLectura,
        "ruido": sensorRuido,
        "ubicacion": sensorUbicacion,
        "estado": sensorEstado,
        "promedio": sensorPromedio
    }
    
    # Actualizar el sensor
    sensor_service.actualizar_sensor(db, sensorId, sensor_data)
    
    # CORREGIDO: Redirigir a /sensores en lugar de renderizar template
    return RedirectResponse("/sensores", status_code=303)