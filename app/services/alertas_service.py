from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from database import Alerta, AlertaView, User, Sensor, Lectura, Parcela

class AlertaService:
    @staticmethod
    def generar_alerta(db, sensor, lectura, tipo, tiempo_minimo=3600):
        """Genera una alerta si no ha ocurrido otra del mismo tipo en el tiempo mínimo."""
        ultima_alerta = db.query(Alerta).filter(
            Alerta.id_sensor == sensor.id,
            Alerta.tipo == tipo,
            Alerta.is_active == True
        ).order_by(Alerta.timestamp.desc()).first()

        if ultima_alerta and (datetime.now() - ultima_alerta.timestamp).total_seconds() < tiempo_minimo:
            return None  # No generar alerta si ya ocurrió recientemente

        nueva_alerta = Alerta(
            id_sensor=sensor.id,
            id_lectura=lectura.id,
            id_parcela=sensor.parcela_id,
            tipo=tipo,
            is_active=True,
            timestamp=datetime.now()
        )
        db.add(nueva_alerta)
        db.commit()

        # Crear vistas para los usuarios
        usuarios = db.query(User).filter(
            (User.role == "tecnico") | (User.role == "agronomo") | (User.parcela_id == sensor.parcela_id)
        ).all()

        for usuario in usuarios:
            alerta_view = AlertaView(
                id_alerta=nueva_alerta.id,
                id_user=usuario.id
            )
            db.add(alerta_view)

        db.commit()
        return nueva_alerta

    @staticmethod
    def comprobar_lecturas(db, sensor, lectura):
        """Comprobar si una lectura excede los umbrales y generar una alerta."""
        parcela = db.query(Parcela).filter(Parcela.id == sensor.parcela_id).first()
        if not parcela:
            return

        # Comprobar umbrales según el tipo de sensor
        if sensor.tipo == "temperatura":
            if lectura.valor < parcela.temperatura_min or lectura.valor > parcela.temperatura_max:
                AlertaService.generar_alerta(db, sensor, lectura, "temperatura")
        elif sensor.tipo == "humedad":
            if lectura.valor < parcela.humedad_min or lectura.valor > parcela.humedad_max:
                AlertaService.generar_alerta(db, sensor, lectura, "humedad")
        elif sensor.tipo == "ph":
            if lectura.valor < parcela.ph_min or lectura.valor > parcela.ph_max:
                AlertaService.generar_alerta(db, sensor, lectura, "ph")