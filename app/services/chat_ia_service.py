import json
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from database import ChatIA
from models.chat_ia import ChatIACreate, ChatIAUpdate, ChatIAResponse, ChatIAListItem, MessageData

class ChatIAService:
    
    @staticmethod
    def generate_chat_id() -> str:
        """Genera un ID único para el chat"""
        return f"chat_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
    
    @staticmethod
    def create_chat(db: Session, user_id: int, chat_data: ChatIACreate) -> ChatIA:
        """Crea un nuevo chat IA"""
        chat_id = ChatIAService.generate_chat_id()
        
        # Serializar mensajes a JSON
        messages_json = json.dumps([msg.dict() for msg in chat_data.messages])
        
        db_chat = ChatIA(
            id=chat_id,
            user_id=user_id,
            title=chat_data.title,
            messages=messages_json,
            timestamp=datetime.now(),
            last_modified=datetime.now()
        )
        
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat
    
    @staticmethod
    def get_chat_by_id(db: Session, chat_id: str, user_id: int) -> Optional[ChatIA]:
        """Obtiene un chat por ID (verificando que pertenezca al usuario)"""
        return db.query(ChatIA).filter(
            ChatIA.id == chat_id, 
            ChatIA.user_id == user_id,
            ChatIA.is_active == True
        ).first()
    
    @staticmethod
    def get_user_chats(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatIA]:
        """Obtiene todos los chats de un usuario"""
        return db.query(ChatIA).filter(
            ChatIA.user_id == user_id,
            ChatIA.is_active == True
        ).order_by(ChatIA.last_modified.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_chat(db: Session, chat_id: str, user_id: int, chat_data: ChatIAUpdate) -> Optional[ChatIA]:
        """Actualiza un chat existente"""
        db_chat = ChatIAService.get_chat_by_id(db, chat_id, user_id)
        if not db_chat:
            return None
        
        if chat_data.title is not None:
            db_chat.title = chat_data.title
        
        if chat_data.messages is not None:
            db_chat.messages = json.dumps([msg.dict() for msg in chat_data.messages])
        
        db_chat.last_modified = datetime.now()
        db.commit()
        db.refresh(db_chat)
        return db_chat
    
    @staticmethod
    def save_or_update_chat(db: Session, user_id: int, chat_id: Optional[str], title: str, messages: List[MessageData]) -> ChatIA:
        """Guarda un chat nuevo o actualiza uno existente"""
        if chat_id:
            # Intentar actualizar chat existente
            existing_chat = ChatIAService.get_chat_by_id(db, chat_id, user_id)
            if existing_chat:
                existing_chat.title = title
                existing_chat.messages = json.dumps([msg.dict() for msg in messages])
                existing_chat.last_modified = datetime.now()
                db.commit()
                db.refresh(existing_chat)
                return existing_chat
        
        # Crear nuevo chat
        chat_data = ChatIACreate(title=title, messages=messages)
        return ChatIAService.create_chat(db, user_id, chat_data)
    
    @staticmethod
    def delete_chat(db: Session, chat_id: str, user_id: int) -> bool:
        """Elimina un chat (soft delete)"""
        db_chat = ChatIAService.get_chat_by_id(db, chat_id, user_id)
        if not db_chat:
            return False
        
        db_chat.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def clear_user_chats(db: Session, user_id: int) -> int:
        """Elimina todos los chats de un usuario (soft delete)"""
        count = db.query(ChatIA).filter(
            ChatIA.user_id == user_id,
            ChatIA.is_active == True
        ).update({"is_active": False})
        db.commit()
        return count
    
    @staticmethod
    def serialize_chat_response(chat: ChatIA) -> ChatIAResponse:
        """Convierte un chat de DB a respuesta API"""
        messages = json.loads(chat.messages)
        return ChatIAResponse(
            id=chat.id,
            title=chat.title,
            messages=[MessageData(**msg) for msg in messages],
            timestamp=chat.timestamp,
            last_modified=chat.last_modified,
            is_active=chat.is_active
        )
    
    @staticmethod
    def serialize_chat_list_item(chat: ChatIA) -> ChatIAListItem:
        """Convierte un chat de DB a item de lista"""
        messages = json.loads(chat.messages)
        first_user_message = next((msg for msg in messages if msg.get('role') == 'user'), None)
        
        return ChatIAListItem(
            id=chat.id,
            title=chat.title,
            timestamp=chat.timestamp,
            last_modified=chat.last_modified,
            message_count=len(messages),
            first_message_preview=first_user_message.get('content')[:100] + '...' if first_user_message and len(first_user_message.get('content', '')) > 100 else first_user_message.get('content') if first_user_message else None
        )
    
    @staticmethod
    def get_chat_statistics(db: Session, user_id: int) -> dict:
        """Obtiene estadísticas de chats del usuario"""
        total_chats = db.query(ChatIA).filter(
            ChatIA.user_id == user_id,
            ChatIA.is_active == True
        ).count()
        
        return {
            "total_chats": total_chats,
            "last_chat_date": db.query(ChatIA.last_modified).filter(
                ChatIA.user_id == user_id,
                ChatIA.is_active == True
            ).order_by(ChatIA.last_modified.desc()).first()
        }