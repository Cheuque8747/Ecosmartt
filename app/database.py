# database.py - Actualizado para SQLite con ChatIA
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
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
    
    # Relación con chats IA
    chats_ia = relationship("ChatIA", back_populates="user", cascade="all, delete-orphan")

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

class ChatIA(Base):
    __tablename__ = "chats_ia"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    messages = Column(Text, nullable=False)  # JSON serializado
    timestamp = Column(DateTime, default=datetime.now)
    last_modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Relación con usuario
    user = relationship("User", back_populates="chats_ia")

# Crear las tablas
Base.metadata.create_all(bind=engine)


# Función para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = SessionLocal()
    try:
        # Verificar si ya existe algún usuario
        user = db.query(User).first()
        if not user:
            from services.auth_service import get_password_hash  # Importar la función de hash
            
            # Crear usuario administrador por defecto
            default_user = User(
                username="admin",
                email="admin@ecosmartt.com",
                hashed_password=get_password_hash("admin123"), 
                role="tecnico",
                is_active=True
            )
            db.add(default_user)
            db.commit()
            print("Usuario administrador creado con éxito")
    except Exception as e:
        print(f"Error al crear usuario por defecto: {e}")
        db.rollback()
    finally:
        db.close()

# Llamar a la función de inicialización
init_db()