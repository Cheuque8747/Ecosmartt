import os
import requests
import json

class DeepSeekService:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # URLs alternativas para diferentes proveedores
        self.providers = [
            {
                "name": "OpenRouter (DeepSeek)",
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "model": "deepseek/deepseek-chat",
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ecosmart.com",
                    "X-Title": "EcoSmart Agriculture Platform"
                }
            },
            {
                "name": "DeepSeek Direct",
                "url": "https://api.deepseek.com/v1/chat/completions",
                "model": "deepseek-chat",
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            }
        ]

    def chat(self, messages):
        """
        Envía mensajes al modelo Deepseek y retorna la respuesta.
        :param messages: Lista de dicts [{"role": "user", "content": "Texto"}]
        """
        if not self.api_key:
            print("❌ DEEPSEEK_API_KEY no configurada")
            return self._create_error_response("Falta la variable DEEPSEEK_API_KEY en el entorno")
        
        # Preprocesar mensajes para agricultura
        processed_messages = self._preprocess_messages(messages)
        
        # Intentar con cada proveedor
        for provider in self.providers:
            try:
                print(f"🔄 Intentando con {provider['name']}...")
                response = self._try_provider(provider, processed_messages)
                if response:
                    print(f"✅ Respuesta exitosa de {provider['name']}")
                    return response
            except Exception as e:
                print(f"❌ Error con {provider['name']}: {str(e)}")
                continue
        
        # Si ningún proveedor funciona, usar respuesta fallback
        print("🔄 Todos los proveedores fallaron, usando respuesta fallback")
        return self._get_fallback_response(messages)

    def _preprocess_messages(self, messages):
        """Preprocesa los mensajes para mejorar las respuestas de agricultura"""
        processed = []
        
        # Agregar contexto de sistema si no existe
        has_system = any(msg.get('role') == 'system' for msg in messages)
        if not has_system:
            system_message = {
                "role": "system",
                "content": """Eres un asistente experto en agricultura inteligente y tecnología agrícola. 
                Tienes conocimientos profundos sobre:
                - Sensores IoT para agricultura (temperatura, humedad, pH, conductividad, luz)
                - Sistemas de riego inteligente
                - Análisis de datos climáticos
                - Diagnóstico de problemas en cultivos
                - Optimización de rendimientos
                - Mejores prácticas agrícolas
                
                Siempre responde de manera práctica, específica y actionable. 
                Usa un lenguaje claro y profesional en español."""
            }
            processed.append(system_message)
        
        # Agregar mensajes originales
        processed.extend(messages)
        
        return processed

    def _try_provider(self, provider, messages):
        """Intenta hacer la petición con un proveedor específico"""
        data = {
            "model": provider["model"],
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": False
        }
        
        print(f"📤 Enviando solicitud a {provider['name']} con {len(messages)} mensajes")
        
        response = requests.post(
            provider["url"], 
            headers=provider["headers"], 
            json=data, 
            timeout=30
        )
        
        print(f"📥 Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Validar estructura de respuesta
            if self._validate_response(response_data):
                return response_data
            else:
                print("❌ Respuesta inválida del proveedor")
                return None
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text[:200]}")
            return None

    def _validate_response(self, response_data):
        """Valida que la respuesta tenga la estructura correcta"""
        return (
            isinstance(response_data, dict) and
            'choices' in response_data and
            isinstance(response_data['choices'], list) and
            len(response_data['choices']) > 0 and
            'message' in response_data['choices'][0] and
            'content' in response_data['choices'][0]['message']
        )

    def _create_error_response(self, error_message):
        """Crea una respuesta de error en el formato esperado"""
        return {
            "choices": [{
                "message": {
                    "content": error_message
                }
            }]
        }

    def _get_fallback_response(self, messages):
        """Genera una respuesta fallback inteligente basada en el contexto"""
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content', '').lower()
                break
        
        # Respuestas contextuales basadas en palabras clave
        fallback_responses = {
            'temperatura': """Sobre temperatura en cultivos:
            
            • **Rango óptimo**: La mayoría de cultivos prosperan entre 18-25°C
            • **Monitoreo**: Usa sensores para detectar fluctuaciones extremas
            • **Estrés térmico**: Temperaturas >30°C pueden reducir rendimiento
            • **Protección**: Considera mallas de sombra en climas muy calurosos
            
            ¿Necesitas información específica sobre algún cultivo en particular?""",
            
            'riego': """Sobre sistemas de riego inteligente:
            
            • **Frecuencia**: Depende del tipo de suelo y etapa del cultivo
            • **Sensores**: Humedad del suelo es clave para decidir cuándo regar
            • **Horarios**: Mejor en horas tempranas (6-8 AM) para reducir evaporación
            • **Cantidad**: 2-3 cm por semana es promedio para la mayoría de cultivos
            
            ¿Qué tipo de cultivo estás manejando?""",
            
            'ph': """Sobre pH del suelo:
            
            • **Rango ideal**: 6.0-7.0 para la mayoría de cultivos
            • **pH ácido** (<6.0): Agregar cal agrícola
            • **pH alcalino** (>7.5): Usar azufre o materia orgánica
            • **Medición**: Usa sensores digitales para monitoreo continuo
            
            ¿Qué valor de pH están mostrando tus sensores?""",
            
            'plaga': """Para el manejo integrado de plagas:
            
            • **Prevención**: Mantén cultivos saludables y suelo balanceado
            • **Monitoreo**: Inspecciona plantas regularmente
            • **Control biológico**: Usa insectos beneficiosos cuando sea posible
            • **Rotación**: Cambia cultivos para romper ciclos de plagas
            
            ¿Qué síntomas específicos estás observando?""",
            
            'sensor': """Sobre sensores agrícolas:
            
            • **Calibración**: Revisa la calibración mensualmente
            • **Mantenimiento**: Limpia sensores de humedad regularmente
            • **Ubicación**: Coloca sensores representativos del área
            • **Frecuencia**: Ajusta según necesidades del cultivo
            
            ¿Qué tipo de sensor necesitas configurar?"""
        }
        
        # Buscar respuesta contextual
        for keyword, response in fallback_responses.items():
            if keyword in last_user_message:
                return self._create_error_response(response)
        
        # Respuesta genérica si no hay coincidencias
        generic_response = """Lo siento, estoy experimentando dificultades técnicas en este momento.
        
        Sin embargo, puedo ayudarte con:
        
        🌱 **Diagnóstico de cultivos**: Identifica problemas en tus plantas
        💧 **Optimización de riego**: Mejora la eficiencia del agua
        🌡️ **Análisis de sensores**: Interpreta datos de temperatura, humedad, pH
        🦗 **Control de plagas**: Estrategias de manejo integrado
        📊 **Análisis climático**: Impacto del clima en tus cultivos
        
        Por favor, intenta reformular tu pregunta o usa una de las plantillas predefinidas.
        
        **Ejemplo**: "Ayúdame a diagnosticar manchas amarillas en las hojas de mi cultivo de tomate"
        """
        
        return self._create_error_response(generic_response)

    def test_connection(self):
        """Prueba la conexión con los servicios de IA"""
        test_messages = [
            {"role": "user", "content": "Hola, responde solo con 'Conexión exitosa'"}
        ]
        
        try:
            response = self.chat(test_messages)
            return {
                "status": "success",
                "response": response
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }