from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import Alerta, AlertaView, get_db, Parcela, Lectura
from services.auth_service import get_current_active_user
from config import templates


router = APIRouter(prefix="/alertas", tags=["Alertas"])

@router.get("/historial", response_class=HTMLResponse)
async def historial_alertas(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Muestra el historial completo de alertas para el usuario actual."""
    alertas = db.query(Alerta).join(AlertaView).filter(
        AlertaView.id_user == current_user.id
    ).order_by(Alerta.timestamp.desc()).all()

    # Agregar información adicional y calcular urgencia
    alertas_con_urgencia = []
    for alerta in alertas:
        lectura = db.query(Lectura).filter(Lectura.id == alerta.id_lectura).first()
        parcela = db.query(Parcela).filter(Parcela.id == alerta.id_parcela).first()

        # Calcular urgencia según los umbrales de la parcela
        if alerta.tipo == "temperatura":
            if lectura.valor < parcela.temperatura_min or lectura.valor > parcela.temperatura_max:
                urgencia = "Alta"
            else:
                urgencia = "Normal"
        elif alerta.tipo == "humedad":
            if lectura.valor < parcela.humedad_min or lectura.valor > parcela.humedad_max:
                urgencia = "Alta"
            else:
                urgencia = "Normal"
        elif alerta.tipo == "ph":
            if lectura.valor < parcela.ph_min or lectura.valor > parcela.ph_max:
                urgencia = "Alta"
            else:
                urgencia = "Normal"
        else:
            urgencia = "Desconocida"

        # Agregar información adicional
        alertas_con_urgencia.append({
            "id": alerta.id,
            "tipo": alerta.tipo,
            "parcela_nombre": parcela.nombre,
            "sensor_id": alerta.id_sensor,
            "lectura_valor": lectura.valor,
            "lectura_unidad": lectura.unidad,
            "timestamp": alerta.timestamp,
            "urgencia": urgencia,
            "is_vista": any(view.is_vista for view in alerta.vistas if view.id_user == current_user.id)
        })

    return templates.TemplateResponse("historial_alertas.html", {
        "request": request,
        "alertas": alertas_con_urgencia,
        "user": current_user
    })


@router.get("/no-vistas", response_class=HTMLResponse)
async def alertas_no_vistas(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtiene las alertas no vistas para el usuario actual."""
    alertas = db.query(Alerta).join(AlertaView).filter(
        AlertaView.id_user == current_user.id,  # Cambiado a current_user.id
        AlertaView.is_vista == False
    ).order_by(Alerta.timestamp.desc()).limit(5).all()
    return templates.TemplateResponse("alertas_no_vistas.html", {"request": request, "alertas": alertas, "user": current_user})

@router.post("/marcar-vistas")
async def marcar_alertas_vistas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Marca todas las alertas no vistas como vistas para el usuario actual."""
    db.query(AlertaView).filter(
        AlertaView.id_user == current_user.id,  # Cambiado a current_user.id
        AlertaView.is_vista == False
    ).update({"is_vista": True})
    db.commit()
    return {"message": "Alertas marcadas como vistas"}

@router.get("/cantidad-no-vistas", response_model=dict)
async def cantidad_alertas_no_vistas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Devuelve la cantidad de alertas no vistas para el usuario actual."""
    cantidad = db.query(AlertaView).filter(
        AlertaView.id_user == current_user.id,
        AlertaView.is_vista == False
    ).count()
    return {"cantidad": cantidad}

@router.post("/marcar-vista/{alerta_id}")
async def marcar_alerta_vista(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Marca una alerta como vista."""
    alerta_view = db.query(AlertaView).filter(
        AlertaView.id_alerta == alerta_id,
        AlertaView.id_user == current_user.id
    ).first()

    if alerta_view:
        alerta_view.is_vista = True
        db.commit()

    return {"message": "Alerta marcada como vista"}