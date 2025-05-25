from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Módulos actualizados
from routers import sensores, lecturas, auth, ia, clima, parcelas
from routers.auth import get_current_active_user

from config import templates, sensor_info
from database import get_db, Sensor, Base, engine

from pathlib import Path
from datetime import datetime
import threading
from sqlalchemy.orm import Session
from typing import Optional
from services.auth_service import get_current_active_user


# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EcoSmart - Plataforma de Agricultura Inteligente")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(auth.router, prefix="/auth")
app.include_router(sensores.router)
app.include_router(lecturas.router)
app.include_router(ia.router)
app.include_router(clima.router)
app.include_router(parcelas.router)

from database import Parcela
from fastapi import Query
#HTTPException
from fastapi.exceptions import HTTPException

# Rutas para la API
@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_active_user),
    parcela_id: Optional[str] = Query(None),  # Cambiar a Optional[str] para aceptar cadenas vacías
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    ubicacion: Optional[str] = None
):
    # Convertir cadena vacía a None
    if parcela_id == "":
        parcela_id = None
    else:
        parcela_id = int(parcela_id) if parcela_id else None

    """Renderiza la página principal con sensores filtrados según el rol del usuario"""
    if not current_user:
        return RedirectResponse(url="/auth/login")

    # Filtrar sensores según el rol del usuario
    if current_user.role == "agricultor":
        # Solo mostrar sensores de la parcela del agricultor
        if not current_user.parcela_id:
            raise HTTPException(status_code=403, detail="No tienes una parcela asignada")
        sensores = db.query(Sensor).filter(Sensor.parcela_id == current_user.parcela_id).all()
        parcelas = [db.query(Parcela).get(current_user.parcela_id)]
    else:
        # Técnicos y agrónomos pueden ver todas las parcelas
        parcelas = db.query(Parcela).all()
        if parcela_id:
            sensores = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
        else:
            sensores = db.query(Sensor).all()

    # Aplicar filtros adicionales
    if tipo:
        sensores = [s for s in sensores if s.tipo == tipo]
    if estado:
        sensores = [s for s in sensores if s.estado == estado]
    if ubicacion:
        sensores = [s for s in sensores if ubicacion.lower() in s.ubicacion.lower()]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "sensores": sensores,
            "sensor_info": sensor_info,
            "parcelas": parcelas,
            "parcela_id": parcela_id,
            "user": current_user
        }
    )

# Función para iniciar el thread de generación de lecturas
def iniciar_generacion_lecturas():
    from services.lecturas_service import generar_lecturas_periodicamente
    from database import SessionLocal
    
    # Crear una sesión específica para este thread
    db = SessionLocal()
    try:
        generar_lecturas_periodicamente(db, sensor_info)
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando inicia la aplicación"""
    # Crear un thread que ejecute la generación periódica de lecturas
    thread = threading.Thread(target=iniciar_generacion_lecturas, daemon=True)
    thread.start()
    print("Proceso de generación automática de lecturas iniciado en segundo plano")

# Detener el proceso cuando se cierra la aplicación
@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta cuando se cierra la aplicación"""
    print("Deteniendo proceso de generación automática de lecturas")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)