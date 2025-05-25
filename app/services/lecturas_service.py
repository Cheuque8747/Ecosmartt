import random
from sqlalchemy.orm import Session
from database import Sensor, Lectura
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import desc

def cargar_historial_lecturas(db: Session, sensor_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Carga el historial de lecturas desde la base de datos"""
    result = {}
    
    # Consulta base
    query = db.query(Lectura)
    
    # Si se proporciona un ID de sensor, filtrar por ese sensor
    if sensor_id:
        lecturas = query.filter(Lectura.sensor_id == sensor_id).order_by(desc(Lectura.timestamp)).all()
        
        # Convertir a formato de diccionario para mantener compatibilidad con código existente
        result[sensor_id] = [{
            "valor": lectura.valor,
            "timestamp": lectura.timestamp.isoformat(),
            "unidad": lectura.unidad,
            "tipo": lectura.tipo
        } for lectura in lecturas]
    else:
        # Obtener todas las lecturas agrupadas por sensor_id
        lecturas = query.order_by(desc(Lectura.timestamp)).all()
        
        # Agrupar por sensor_id
        for lectura in lecturas:
            if lectura.sensor_id not in result:
                result[lectura.sensor_id] = []
            
            result[lectura.sensor_id].append({
                "valor": lectura.valor,
                "timestamp": lectura.timestamp.isoformat(),
                "unidad": lectura.unidad,
                "tipo": lectura.tipo
            })
    
    return result

def guardar_lectura(db: Session, sensor_id: str, valor: float, timestamp: datetime, unidad: str, tipo_sensor: str) -> Lectura:
    """Guarda una lectura en la base de datos"""
    # Crear nueva lectura
    nueva_lectura = Lectura(
        sensor_id=sensor_id,
        valor=round(float(valor), 2),
        timestamp=timestamp,
        unidad=unidad,
        tipo=tipo_sensor
    )
    
    # Guardar en la base de datos
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)
    
    # Verificar si hay más de 100 lecturas para este sensor
    count = db.query(Lectura).filter(Lectura.sensor_id == sensor_id).count()
    
    # Si hay más de 100, eliminar las más antiguas
    if count > 100:
        # Obtener las lecturas más antiguas que exceden el límite
        lecturas_antiguas = db.query(Lectura).filter(Lectura.sensor_id == sensor_id).order_by(Lectura.timestamp).limit(count - 100).all()
        
        # Eliminar las lecturas antiguas
        for lectura in lecturas_antiguas:
            db.delete(lectura)
        
        db.commit()
    
    return nueva_lectura

def generar_lectura(db: Session, sensor: Sensor, ignore_time_check: bool = False) -> Optional[float]:
    """Genera una lectura simulada para un sensor basada en sus parámetros"""
    if sensor.estado != "activo":
        return None
    
    # Verificamos si es el momento de generar una nueva lectura (a menos que se ignore este control)
    if not ignore_time_check and sensor.ultima_medicion:
        tiempo_transcurrido = (datetime.now() - sensor.ultima_medicion).total_seconds()
        if tiempo_transcurrido < sensor.frecuencia_lectura:
            return None 
    
    # Generamos una lectura alrededor del promedio configurado y calculamos un rango de variación basado en el ruido y el rango min-max
    variacion = (sensor.max_lectura - sensor.min_lectura) * 0.1  
    if sensor.ruido > 0:
        variacion = max(variacion, sensor.ruido)
    
    # Generamos una lectura alrededor del promedio con la variación calculada
    lectura = sensor.promedio + random.uniform(-variacion, variacion)
    
    # Aseguramos que el valor esté dentro de los límites
    lectura = max(sensor.min_lectura, min(lectura, sensor.max_lectura))
    
    # Redondeamos a 2 decimales
    return round(lectura, 2)

def generar_lecturas_periodicamente(db: Session, sensor_info: Dict[str, Dict[str, str]]):
    """Función que genera lecturas periódicamente para todos los sensores activos"""
    print("Iniciando generación automática de lecturas con SQLite...")
    
    while True:
        # Obtener todos los sensores activos
        sensores_activos = db.query(Sensor).filter(Sensor.estado == "activo").all()
        
        for sensor in sensores_activos:
            if sensor.ultima_medicion:
                # Calculamos si es tiempo de generar una lectura
                tiempo_transcurrido = (datetime.now() - sensor.ultima_medicion).total_seconds()
                if tiempo_transcurrido >= sensor.frecuencia_lectura:
                    lectura = generar_lectura(db, sensor)
                    
                    if lectura is not None:
                        timestamp = datetime.now()
                        
                        # Actualizamos el sensor
                        sensor.ultima_medicion = timestamp
                        db.commit()
                        
                        # Guardamos la lectura en la base de datos
                        unidad = sensor_info[sensor.tipo]["unit"]
                        guardar_lectura(db, sensor.id, lectura, timestamp, unidad, sensor.tipo)
                        
                        print(f"Lectura generada para sensor {sensor.id}: {lectura} {unidad}")
        
        # Esperamos un tiempo antes de la siguiente verificación (10 segundos)
        import time
        time.sleep(10)

def obtener_lecturas_sensor(db: Session, sensor_id: str, limit: int = 100) -> List[Lectura]:
    """Obtiene las lecturas de un sensor específico"""
    return db.query(Lectura).filter(Lectura.sensor_id == sensor_id).order_by(desc(Lectura.timestamp)).limit(limit).all()

def obtener_lecturas_sensor_paginadas(db: Session, sensor_id: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Obtiene las lecturas de un sensor con paginación"""
    # Calcular offset
    offset = (page - 1) * per_page
    
    # Obtener lecturas paginadas
    lecturas = db.query(Lectura).filter(Lectura.sensor_id == sensor_id).order_by(desc(Lectura.timestamp)).offset(offset).limit(per_page).all()
    
    # Obtener total de lecturas para calcular páginas
    total_lecturas = db.query(Lectura).filter(Lectura.sensor_id == sensor_id).count()
    total_pages = (total_lecturas + per_page - 1) // per_page  # Redondear hacia arriba
    
    return {
        "lecturas": lecturas,
        "page": page,
        "per_page": per_page,
        "total_lecturas": total_lecturas,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages
    }

def obtener_estadisticas_sensor(db: Session, sensor_id: str) -> Dict[str, float]:
    """Obtiene estadísticas de las lecturas de un sensor"""
    lecturas = obtener_lecturas_sensor(db, sensor_id)
    
    if not lecturas:
        return {
            "min_valor": 0,
            "max_valor": 0,
            "promedio_valor": 0
        }
    
    valores = [lectura.valor for lectura in lecturas]
    
    return {
        "min_valor": min(valores),
        "max_valor": max(valores),
        "promedio_valor": sum(valores) / len(valores)
    }