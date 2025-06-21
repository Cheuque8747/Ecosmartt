from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from config import templates
from services.deepseek_service import DeepSeekService
from services.auth_service import get_current_active_user
from database import User, Parcela
from sqlalchemy.orm import Session
from database import get_db
import os
import traceback

router = APIRouter(prefix="/ia", tags=["IA"])


import json
@router.get("/chat", response_class=HTMLResponse)
async def ia_chat_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Obtener las parcelas según el rol del usuario
    if current_user.role == "agricultor":
        parcelas = db.query(Parcela).filter(Parcela.id == current_user.parcela_id).all()
    else:
        parcelas = db.query(Parcela).all()

    # Convertir parcelas a formato JSON
    parcelas_json = [{"id": p.id, "nombre": p.nombre, "ubicacion": p.ubicacion} for p in parcelas]

    return templates.TemplateResponse(
        "ia_chat.html",
        {"request": request, "user": current_user, "parcelas": parcelas, "parcelas_json": json.dumps(parcelas_json)}
    )

@router.post("/chat")
async def ia_chat_api(request: Request):
    try:
        # Obtener datos del request
        data = await request.json()
        messages = data.get("messages", [])
        
        print(f"🔍 Recibida petición con {len(messages)} mensajes")
        
        if not messages:
            print("❌ No se proporcionaron mensajes")
            return JSONResponse(
                status_code=400,
                content={"error": "No se proporcionaron mensajes"}
            )
        
        # Verificar configuración de API
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ DEEPSEEK_API_KEY no configurada")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Servicio de IA no configurado",
                    "choices": [{
                        "message": {
                            "content": """⚠️ **Servicio de IA no disponible**
                            
El servicio de inteligencia artificial no está configurado correctamente.

**Mientras tanto, puedo ayudarte con:**

🌱 **Consejos generales de agricultura:**
• Mantén el pH del suelo entre 6.0-7.0
• Riega en horas tempranas para reducir evaporación
• Monitorea temperatura: 18-25°C es ideal para la mayoría de cultivos

💧 **Riego inteligente:**
• Usa sensores de humedad del suelo
• Ajusta frecuencia según etapa del cultivo
• 2-3 cm de agua por semana es promedio

🌡️ **Interpretación de sensores:**
• Temperatura >30°C: Riesgo de estrés térmico
• Humedad <30%: Necesidad de riego
• pH <6.0: Suelo ácido, agregar cal

Por favor, contacta al administrador para configurar el servicio de IA."""
                        }
                    }]
                }
            )
        
        print(f"✅ API Key configurada: {api_key[:10]}...")
        
        # Inicializar servicio de IA
        deepseek = DeepSeekService()
        
        print("🚀 Enviando mensajes a DeepSeek...")
        
        # Procesar con el servicio de IA
        respuesta = deepseek.chat(messages)
        
        print(f"📦 Respuesta recibida: {type(respuesta)}")
        
        # Validar respuesta
        if not respuesta:
            print("❌ Respuesta vacía de DeepSeek")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Respuesta vacía del servicio de IA",
                    "choices": [{
                        "message": {
                            "content": "Lo siento, no pude generar una respuesta en este momento. Por favor, intenta de nuevo."
                        }
                    }]
                }
            )
        
        # Verificar estructura de respuesta
        if not isinstance(respuesta, dict) or 'choices' not in respuesta:
            print(f"❌ Estructura de respuesta inválida: {respuesta}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Formato de respuesta inválido",
                    "choices": [{
                        "message": {
                            "content": "Recibí una respuesta en formato incorrecto del servicio de IA. Por favor, intenta de nuevo."
                        }
                    }]
                }
            )
        
        print("✅ Respuesta válida, enviando al cliente")
        return JSONResponse(content=respuesta)
        
    except ValueError as ve:
        error_msg = f"Error de configuración: {str(ve)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": error_msg,
                "choices": [{
                    "message": {
                        "content": f"Error de configuración del servicio: {str(ve)}"
                    }
                }]
            }
        )
    except Exception as e:
        error_msg = f"Error interno del servidor: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": error_msg,
                "choices": [{
                    "message": {
                        "content": f"""🔧 **Error técnico detectado**

Ha ocurrido un error interno en el sistema.

**Sugerencias para resolverlo:**
• Intenta recargar la página
• Verifica tu conexión a internet
• Si el problema persiste, contacta al administrador

**Error técnico:** {str(e)[:100]}...

**Mientras tanto, aquí tienes algunos consejos generales:**

🌱 **Monitoreo de cultivos:**
• Revisa sensores diariamente
• Mantén registros de lecturas anómalas
• Ajusta parámetros según temporada

💧 **Gestión del agua:**
• Programa riegos en horas frescas
• Monitorea humedad del suelo constantemente
• Ajusta frecuencia según clima"""
                    }
                }]
            }
        )

@router.get("/test")
async def test_ia_connection():
    """Endpoint para probar la conexión con la IA"""
    try:
        # Verificar variable de entorno
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "DEEPSEEK_API_KEY no configurada",
                    "solution": "Configura la variable de entorno DEEPSEEK_API_KEY",
                    "details": {
                        "env_vars_found": list(os.environ.keys()),
                        "expected_var": "DEEPSEEK_API_KEY"
                    }
                }
            )
        
        print(f"🔍 Probando conexión con API Key: {api_key[:10]}...")
        
        # Probar conexión con mensaje simple
        deepseek = DeepSeekService()
        result = deepseek.test_connection()
        
        if result["status"] == "success":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Conexión con IA funcionando correctamente",
                    "response": result["response"],
                    "api_key_preview": f"{api_key[:10]}...{api_key[-4:]}"
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error en la conexión: {result['message']}",
                    "solution": "Verifica la configuración de DEEPSEEK_API_KEY"
                }
            )
        
    except Exception as e:
        print(f"❌ Error en test de conexión: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error inesperado en test: {str(e)}",
                "solution": "Verifica la configuración del sistema",
                "traceback": traceback.format_exc()
            }
        )
    

from fastapi import HTTPException
from database import Sensor
from services.openweather_service import OpenWeatherService
weather_service = OpenWeatherService()

@router.get("/sensores/promedios")  # riego
async def obtener_promedios_sensores(
    parcela_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sensores = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
    if not sensores:
        raise HTTPException(status_code=404, detail="No se encontraron sensores para la parcela seleccionada.")

    promedios = {}
    for tipo in ["humedad", "temperatura", "conductividad", "ph"]:
        lecturas = [lectura.valor for sensor in sensores if sensor.tipo == tipo for lectura in sensor.lecturas]
        if lecturas:
            promedios[tipo] = round(sum(lecturas) / len(lecturas), 2)  # Limitar a 2 decimales
        else:
            promedios[tipo] = None  # No hay lecturas disponibles
            print(f"No hay lecturas disponibles para el tipo {tipo} en la parcela {parcela_id}")

    return promedios


@router.get("/clima/actual-pronostico") #clima
async def obtener_clima_actual(
    parcela_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene el clima actual y el pronóstico para una parcela específica."""
    parcela = db.query(Parcela).filter(Parcela.id == parcela_id).first()
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela no encontrada.")

    #coordenadas = parcela.ubicacion

    lat, lon = map(float, parcela.ubicacion.split(",")) 

    print(f"🔍 Obteniendo clima para parcela {parcela_id} en coordenadas: {lat}, {lon}")
    clima_actual = weather_service.get_current_weather_by_coords(lat , lon)
    pronostico = weather_service.get_forecast_by_coords(lat , lon)

    return {
        "clima_actual": clima_actual,
        "pronostico": pronostico
    }

@router.get("/sensores/ultimas_lecturas") #plagas
async def obtener_ultimas_lecturas(
    parcela_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene las últimas lecturas de humedad y temperatura para una parcela específica."""
    sensores = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
    if not sensores:
        raise HTTPException(status_code=404, detail="No se encontraron sensores para la parcela seleccionada.")

    ultimas_lecturas = {}
    for tipo in ["humedad", "temperatura"]:
        sensor = next((s for s in sensores if s.tipo == tipo), None)
        if sensor and sensor.lecturas:
            ultima_lectura = max(sensor.lecturas, key=lambda l: l.timestamp)
            ultimas_lecturas[tipo] = {
                "valor": round(ultima_lectura.valor, 2),
                "timestamp": ultima_lectura.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            ultimas_lecturas[tipo] = None

    return ultimas_lecturas


@router.get("/sensores/promedios_fertilizacion") # fertilizacion
async def obtener_promedios_fertilizacion(
    parcela_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene los valores promedio de conductividad y pH para una parcela específica."""
    sensores = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
    if not sensores:
        raise HTTPException(status_code=404, detail="No se encontraron sensores para la parcela seleccionada.")

    promedios = {}
    for tipo in ["conductividad", "ph"]:
        lecturas = [lectura.valor for sensor in sensores if sensor.tipo == tipo for lectura in sensor.lecturas]
        if lecturas:
            promedios[tipo] = round(sum(lecturas) / len(lecturas), 2)  # Limitar a 2 decimales
        else:
            promedios[tipo] = None

    return promedios

@router.get("/sensores/promedios_cosecha")
async def obtener_promedios_cosecha(
    parcela_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene los valores promedio de humedad y temperatura para una parcela específica."""
    sensores = db.query(Sensor).filter(Sensor.parcela_id == parcela_id).all()
    if not sensores:
        raise HTTPException(status_code=404, detail="No se encontraron sensores para la parcela seleccionada.")

    promedios = {}
    for tipo in ["humedad", "temperatura"]:
        lecturas = [lectura.valor for sensor in sensores if sensor.tipo == tipo for lectura in sensor.lecturas]
        if lecturas:
            promedios[tipo] = round(sum(lecturas) / len(lecturas), 2)  # Limitar a 2 decimales
        else:
            promedios[tipo] = None

    return promedios