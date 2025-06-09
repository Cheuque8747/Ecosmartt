from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from config import templates
from database import Parcela, get_db
from services.auth_service import get_current_active_user


from database import User
from typing import Optional
from fastapi import Query
#from models.user import User
from services.auth_service import get_password_hash

router = APIRouter(prefix="/parcelas", tags=["Parcelas"])

# Vista de listado y creación
@router.get("/vista", response_class=HTMLResponse)
def listar_parcelas(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No autorizado")
    parcelas = db.query(Parcela).all()
    return templates.TemplateResponse("parcelas.html", {"request": request, "parcelas": parcelas, "user": current_user})

@router.post("/crear", response_class=RedirectResponse)
def crear_parcela(
    nombre: str = Form(...),
    ubicacion: str = Form(...),
    temperatura_min: float = Form(0.0),
    temperatura_max: float = Form(0.0),
    humedad_min: float = Form(0.0),
    humedad_max: float = Form(0.0),
    ph_min: float = Form(0.0),
    ph_max: float = Form(0.0),
    temperatura_active: bool = Form(False),
    humedad_active: bool = Form(False),
    ph_active: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No autorizado")
    parcela = Parcela(
        nombre=nombre,
        ubicacion=ubicacion,
        temperatura_min=temperatura_min,
        temperatura_max=temperatura_max,
        humedad_min=humedad_min,
        humedad_max=humedad_max,
        ph_min=ph_min,
        ph_max=ph_max,
        temperatura_active=temperatura_active,
        humedad_active=humedad_active,
        ph_active=ph_active
    )
    db.add(parcela)
    db.commit()
    return RedirectResponse("/parcelas/vista", status_code=303)

@router.post("/borrar/{parcela_id}", response_class=RedirectResponse)
def borrar_parcela(parcela_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No autorizado")
    parcela = db.query(Parcela).get(parcela_id)
    if parcela:
        db.delete(parcela)
        db.commit()
    return RedirectResponse("/parcelas/vista", status_code=303)

@router.post("/actualizar/{parcela_id}", response_class=RedirectResponse)
def actualizar_parcela(
    parcela_id: int,
    nombre: str = Form(...),
    ubicacion: str = Form(...),
    temperatura_min: float = Form(...),
    temperatura_max: float = Form(...),
    humedad_min: float = Form(...),
    humedad_max: float = Form(...),
    ph_min: float = Form(...),
    ph_max: float = Form(...),
    temperatura_active: bool = Form(False),
    humedad_active: bool = Form(False),
    ph_active: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    parcela = db.query(Parcela).get(parcela_id)
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela no encontrada")
    
    # Actualizar los valores de la parcela
    parcela.nombre = nombre
    parcela.ubicacion = ubicacion
    parcela.temperatura_min = temperatura_min
    parcela.temperatura_max = temperatura_max
    parcela.humedad_min = humedad_min
    parcela.humedad_max = humedad_max
    parcela.ph_min = ph_min
    parcela.ph_max = ph_max
    parcela.temperatura_active = temperatura_active
    parcela.humedad_active = humedad_active
    parcela.ph_active = ph_active

    db.commit()
    return RedirectResponse("/parcelas/vista", status_code=303)

@router.get("/trabajadores", response_class=HTMLResponse)
def trabajadores_por_parcela(
    request: Request,
    parcela_id: Optional[str] = Query(None, description="ID de la parcela"),  # Cambiar a Optional[str] para aceptar cadenas vacías
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Convertir cadena vacía a None
    if parcela_id == "":
        parcela_id = None
    else:
        parcela_id = int(parcela_id) if parcela_id else None

    if current_user.role == "agricultor":
        # Solo muestra los trabajadores de la parcela del agricultor
        if not current_user.parcela_id:
            raise HTTPException(status_code=403, detail="No tienes una parcela asignada")
        parcela_id = current_user.parcela_id
        trabajadores = db.query(User).filter(User.parcela_id == parcela_id).all()
        parcelas = [db.query(Parcela).get(parcela_id)]
    else:
        # Agrónomos y técnicos pueden ver todas las parcelas
        parcelas = db.query(Parcela).all()
        if parcela_id:
            trabajadores = db.query(User).filter(User.parcela_id == parcela_id).all()
        else:
            trabajadores = db.query(User).all()

    return templates.TemplateResponse(
        "trabajadores_parcela.html",
        {
            "request": request,
            "parcelas": parcelas,
            "trabajadores": trabajadores,
            "parcela_id": parcela_id,
            "user": current_user,
            "role": current_user.role
        }
    )

@router.post("/trabajadores/crear", response_class=RedirectResponse)
def crear_trabajador(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    parcela_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No autorizado")
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password, role=role, parcela_id=parcela_id)
    db.add(user)
    db.commit()
    return RedirectResponse(f"/parcelas/trabajadores?parcela_id={parcela_id}", status_code=303)

@router.post("/trabajadores/borrar/{user_id}", response_class=RedirectResponse)
def borrar_trabajador(
    user_id: int,
    parcela_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No autorizado")
    user = db.query(User).get(user_id)
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(f"/parcelas/trabajadores?parcela_id={parcela_id}", status_code=303)

@router.post("/trabajadores/actualizar/{user_id}", response_class=RedirectResponse)
def actualizar_trabajador(
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    parcela_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No autorizado")
    user = db.query(User).get(user_id)
    if user:
        user.username = username
        user.email = email
        user.role = role
        user.parcela_id = parcela_id
        db.commit()
    return RedirectResponse(f"/parcelas/trabajadores?parcela_id={parcela_id}", status_code=303)