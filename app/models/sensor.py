from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class SensorBase(BaseModel):
    """Modelo base para sensores con atributos comunes"""
    tipo: str = Field(..., description="Tipo de sensor: temperatura, luz solar, ph del suelo, conductividad electrica")
    frecuencia_lectura: int = Field(..., description="Frecuencia de lectura en segundos")
    max_lectura: float = Field(..., description="Valor máximo de lectura")
    min_lectura: float = Field(..., description="Valor mínimo de lectura")
    ruido: float = Field(0.0, description="Ruido aleatorio en las lecturas")
    ubicacion: str = Field(..., description="Ubicación física del sensor")
    estado: str = Field("activo", description="Estado del sensor: activo o noActivo")
    promedio: float = Field(..., description="Valor promedio deseado para las lecturas")
    
    @validator('tipo')
    def tipo_valido(cls, v):
        tipos_validos = ["temperatura", "luz", "ph", "conductividad", "humedad"]
        if v not in tipos_validos:
            raise ValueError(f"Tipo de sensor no válido. Opciones: {tipos_validos}")
        return v
    
    @validator('estado')
    def estado_valido(cls, v):
        if v not in ["activo", "noActivo"]:
            raise ValueError("Estado debe ser 'activo' o 'noActivo'")
        return v
    
    @validator('min_lectura', 'max_lectura')
    def lecturas_validas(cls, v, values):
        if 'min_lectura' in values and 'max_lectura' in values and values['min_lectura'] > v:
            raise ValueError("La lectura máxima debe ser mayor que la mínima")
        return v

class SensorCreate(SensorBase):
    """Modelo para crear un nuevo sensor"""
    pass

class Sensor(SensorBase):
    """Modelo completo de sensor con ID y última medición"""
    id: str = Field(..., description="Identificador único del sensor")
    ultima_medicion: Optional[datetime] = Field(None, description="Timestamp de la última medición")
    
    class Config:
        from_attributes=True
        
class SensorUpdate(BaseModel):
    """Modelo para actualizar un sensor existente"""
    tipo: Optional[str] = None
    frecuencia_lectura: Optional[int] = None
    max_lectura: Optional[float] = None
    min_lectura: Optional[float] = None
    ruido: Optional[float] = None
    ubicacion: Optional[str] = None
    estado: Optional[str] = None

class SensorReading(BaseModel):
    """Modelo para lectura de sensor"""
    sensor_id: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.now)
    unit: str = ""

class SensorReadingHistory(BaseModel):
    """Modelo para el historial de lecturas de un sensor"""
    sensor_id: str
    readings: List[SensorReading]
    sensor_info: Dict[str, Any] = {}

class AlertRule(BaseModel):
    """Modelo para reglas de alertas"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    sensor_id: str
    condicion: str  # 'mayor_que', 'menor_que', 'entre', 'fuera_de'
    valor1: float
    valor2: Optional[float] = None  # Para condiciones 'entre' y 'fuera_de'
    estado: str = "activo"
    prioridad: str = "normal"  # 'baja', 'normal', 'alta', 'critica'
    mensaje: str
    ultima_activacion: Optional[datetime] = None
    
    @validator('condicion')
    def condicion_valida(cls, v):
        condiciones_validas = ["mayor_que", "menor_que", "entre", "fuera_de"]
        if v not in condiciones_validas:
            raise ValueError(f"Condición no válida. Opciones: {condiciones_validas}")
        return v
    
    @validator('valor2')
    def valor2_requerido(cls, v, values):
        if 'condicion' in values and values['condicion'] in ['entre', 'fuera_de'] and v is None:
            raise ValueError("valor2 es requerido para condiciones 'entre' y 'fuera_de'")
        return v

class Alert(BaseModel):
    """Modelo para alertas generadas"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    sensor_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    valor_detectado: float
    mensaje: str
    prioridad: str
    leida: bool = False

class WeatherData(BaseModel):
    """Modelo para datos meteorológicos"""
    ubicacion: str
    temperatura: float
    humedad: float
    presion: float
    velocidad_viento: float
    direccion_viento: float
    descripcion: str
    icon_code: str
    timestamp: datetime = Field(default_factory=datetime.now)
    pronostico: Optional[List[Dict[str, Any]]] = None

# Tipos de unidades para cada tipo de sensor
SENSOR_UNITS = {
    "temperatura": "°C",
    "luz": "lux",
    "ph": "pH",
    "conductividad": "dS/m",
    "humedad": "%"
}

# Íconos para cada tipo de sensor
SENSOR_ICONS = {
    "temperatura": "fas fa-thermometer-half",
    "luz": "fas fa-sun",
    "ph": "fas fa-flask",
    "conductividad": "fas fa-bolt",
    "humedad": "fas fa-tint"
}

# Clases de estilo para cada tipo de sensor
SENSOR_STYLES = {
    "temperatura": "tipo-temperatura",
    "luz": "tipo-luz",
    "ph": "tipo-ph",
    "conductividad": "tipo-conductividad",
    "humedad": "tipo-humedad"
}