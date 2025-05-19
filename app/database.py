
# database.py - Actualizado para SQLite
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
from pathlib import Path

# Crear directorio base para la base de datos
BASE_DIR = Path(__file__).resolve().parent
os.makedirs(BASE_DIR.parent / "data", exist_ok=True)

# Crear motor SQLite
DATABASE_URL = f"sqlite:///{BASE_DIR.parent}/data/ecosmart.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definir modelos
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="tecnico")  # tecnico, agronomo, agricultor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    # Relación con parcelas
    parcela_id = Column(Integer, ForeignKey("parcelas.id"), nullable=True)
    parcela = relationship("Parcela", back_populates="trabajadores")

class Sensor(Base):
    __tablename__ = "sensores"
    
    id = Column(String, primary_key=True, index=True)
    tipo = Column(String, index=True)
    frecuencia_lectura = Column(Integer)
    max_lectura = Column(Float)
    min_lectura = Column(Float)
    ruido = Column(Float, default=0.0)
    ubicacion = Column(String)
    estado = Column(String, default="activo")
    promedio = Column(Float)
    ultima_medicion = Column(DateTime, nullable=True)
    
    # Relación con las lecturas
    lecturas = relationship("Lectura", back_populates="sensor")

    # Relación con la parcela
    parcela_id = Column(Integer, ForeignKey("parcelas.id"), nullable=True)
    parcela = relationship("Parcela", back_populates="sensores")

class Lectura(Base):
    __tablename__ = "lecturas"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, ForeignKey("sensores.id"))
    valor = Column(Float)
    unidad = Column(String)
    tipo = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relación con el sensor
    sensor = relationship("Sensor", back_populates="lecturas")

class Clima(Base):
    __tablename__ = "clima"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    temperatura = Column(Float)
    humedad = Column(Float)
    presion = Column(Float)
    viento = Column(Float)
    descripcion = Column(String)
    icono = Column(String)
    ubicacion = Column(String)

    # Relación con la parcela
    parcela_id = Column(Integer, ForeignKey("parcelas.id"), nullable=True)
    parcela = relationship("Parcela", back_populates="climas")

class Parcela(Base):
    __tablename__ = "parcelas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ubicacion = Column(String, nullable=False)
    
    # Relación con sensores
    sensores = relationship("Sensor", back_populates="parcela")
    # Relación con trabajadores
    trabajadores = relationship("User", back_populates="parcela")
    # Relación con clima
    climas = relationship("Clima", back_populates="parcela")

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Función para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()