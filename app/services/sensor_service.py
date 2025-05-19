from sqlalchemy.orm import Session
from database import Sensor
from datetime import datetime
from typing import List, Optional
from models.sensor import SensorCreate as SensorCreatePydantic

def obtener_sensores(db: Session, skip: int = 0, limit: int = 100) -> List[Sensor]:
    """Obtiene todos los sensores de la base de datos"""
    return db.query(Sensor).offset(skip).limit(limit).all()

def obtener_sensor_por_id(db: Session, sensor_id: str) -> Optional[Sensor]:
    """Obtiene un sensor específico por su ID"""
    return db.query(Sensor).filter(Sensor.id == sensor_id).first()

def filtrar_sensores(db: Session, tipo: Optional[str] = None, estado: Optional[str] = None, 
                    ubicacion: Optional[str] = None) -> List[Sensor]:
    """Filtra sensores según criterios"""
    query = db.query(Sensor)
    
    if tipo:
        query = query.filter(Sensor.tipo == tipo)
    
    if estado:
        query = query.filter(Sensor.estado == estado)
    
    if ubicacion:
        query = query.filter(Sensor.ubicacion.ilike(f"%{ubicacion}%"))
    
    return query.all()

def crear_sensor(db: Session, sensor: SensorCreatePydantic, sensor_id: str, parcela_id: int) -> Sensor:
    """Crea un nuevo sensor en la base de datos"""
    db_sensor = Sensor(
        id=sensor_id,
        tipo=sensor.tipo,
        frecuencia_lectura=sensor.frecuencia_lectura,
        max_lectura=sensor.max_lectura,
        min_lectura=sensor.min_lectura,
        ruido=sensor.ruido,
        ubicacion=sensor.ubicacion,
        estado=sensor.estado,
        promedio=getattr(sensor, 'promedio', (sensor.min_lectura + sensor.max_lectura) / 2),
        ultima_medicion=datetime.now(),
        parcela_id=parcela_id  # Asignar la parcela al sensor
    )
    
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def actualizar_sensor(db: Session, sensor_id: str, sensor_data: dict) -> Optional[Sensor]:
    """Actualiza un sensor existente en la base de datos"""
    db_sensor = obtener_sensor_por_id(db, sensor_id)
    
    if not db_sensor:
        return None
    
    # Actualizar atributos
    for key, value in sensor_data.items():
        if hasattr(db_sensor, key) and value is not None:
            setattr(db_sensor, key, value)
    
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def eliminar_sensor(db: Session, sensor_id: str) -> bool:
    """Elimina un sensor de la base de datos"""
    db_sensor = obtener_sensor_por_id(db, sensor_id)
    
    if not db_sensor:
        return False
    
    db.delete(db_sensor)
    db.commit()
    return True

def cambiar_estado_sensor(db: Session, sensor_id: str) -> Optional[Sensor]:
    """Cambia el estado de un sensor (activo/noActivo)"""
    db_sensor = obtener_sensor_por_id(db, sensor_id)
    
    if not db_sensor:
        return None
    
    # Cambiar estado
    nuevo_estado = "activo" if db_sensor.estado == "noActivo" else "noActivo"
    db_sensor.estado = nuevo_estado
    
    db.commit()
    db.refresh(db_sensor)
    return db_sensor