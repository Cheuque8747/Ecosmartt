from fastapi import APIRouter, Request, Depends, Query, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db, Parcela
from services.auth_service import get_current_active_user
from config import templates
from typing import Optional

router = APIRouter(prefix="/umbrales", tags=["Umbrales"])

@router.get("/vista", response_class=HTMLResponse)
async def vista_umbral_alertas(
    request: Request,
    parcela_id: Optional[str] = Query(None),  # Aceptar cadenas vacías
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    # Convertir cadena vacía a None
    if parcela_id == "":
        parcela_id = None
    else:
        parcela_id = int(parcela_id) if parcela_id else None

    parcelas = db.query(Parcela).all()
    parcela = db.query(Parcela).filter(Parcela.id == parcela_id).first() if parcela_id else None
    return templates.TemplateResponse(
        "umbrales_alertas.html",
        {
            "request": request,
            "parcelas": parcelas,
            "parcela": parcela,
            "parcela_id": parcela_id,
            "user": current_user
        }
    )

@router.post("/actualizar", response_class=RedirectResponse)
def actualizar_umbral_alertas(
    parcela_id: int = Form(...),
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
    
    parcela = db.query(Parcela).filter(Parcela.id == parcela_id).first()
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela no encontrada")
    
    # Actualizar los valores de los umbrales
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
    return RedirectResponse(f"/umbrales/vista?parcela_id={parcela_id}", status_code=303)