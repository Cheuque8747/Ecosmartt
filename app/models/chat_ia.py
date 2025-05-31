from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class MessageData(BaseModel):
    """Modelo para un mensaje individual"""
    role: str = Field(..., description="Rol del mensaje: 'user' o 'assistant'")
    content: str = Field(..., description="Contenido del mensaje")

class ChatIACreate(BaseModel):
    """Modelo para crear un chat IA"""
    title: str = Field(..., description="Título del chat")
    messages: List[MessageData] = Field(..., description="Lista de mensajes")

class ChatIAUpdate(BaseModel):
    """Modelo para actualizar un chat IA"""
    title: Optional[str] = None
    messages: Optional[List[MessageData]] = None

class ChatIAResponse(BaseModel):
    """Modelo de respuesta para chat IA"""
    id: str
    title: str
    messages: List[MessageData]
    timestamp: datetime
    last_modified: datetime
    is_active: bool

    class Config:
        from_attributes = True

class ChatIAListItem(BaseModel):
    """Modelo para lista de chats IA (sin mensajes completos)"""
    id: str
    title: str
    timestamp: datetime
    last_modified: datetime
    message_count: int
    first_message_preview: Optional[str] = None

    class Config:
        from_attributes = True

class ChatIASaveRequest(BaseModel):
    """Modelo para guardar/actualizar chat desde frontend"""
    id: Optional[str] = None
    title: str
    messages: List[MessageData]

class ChatIADeleteRequest(BaseModel):
    """Modelo para eliminar chat"""
    chat_id: str