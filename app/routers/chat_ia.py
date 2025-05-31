from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from database import get_db, User
from services.auth_service import get_current_active_user
from services.chat_ia_service import ChatIAService
from models.chat_ia import (
    ChatIACreate, 
    ChatIAUpdate, 
    ChatIAResponse, 
    ChatIAListItem, 
    ChatIASaveRequest,
    ChatIADeleteRequest
)

router = APIRouter(prefix="/api/chat-ia", tags=["Chat IA"])

@router.get("/history", response_model=List[ChatIAListItem])
async def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene el historial de chats del usuario actual"""
    chats = ChatIAService.get_user_chats(db, current_user.id, skip, limit)
    return [ChatIAService.serialize_chat_list_item(chat) for chat in chats]

@router.get("/{chat_id}", response_model=ChatIAResponse)
async def get_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene un chat específico por ID"""
    chat = ChatIAService.get_chat_by_id(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    return ChatIAService.serialize_chat_response(chat)

@router.post("/save", response_model=ChatIAResponse)
async def save_chat(
    chat_request: ChatIASaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Guarda un chat nuevo o actualiza uno existente"""
    try:
        chat = ChatIAService.save_or_update_chat(
            db=db,
            user_id=current_user.id,
            chat_id=chat_request.id,
            title=chat_request.title,
            messages=chat_request.messages
        )
        return ChatIAService.serialize_chat_response(chat)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar chat: {str(e)}"
        )

@router.post("/", response_model=ChatIAResponse)
async def create_chat(
    chat_data: ChatIACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crea un nuevo chat IA"""
    try:
        chat = ChatIAService.create_chat(db, current_user.id, chat_data)
        return ChatIAService.serialize_chat_response(chat)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear chat: {str(e)}"
        )

@router.put("/{chat_id}", response_model=ChatIAResponse)
async def update_chat(
    chat_id: str,
    chat_data: ChatIAUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualiza un chat existente"""
    chat = ChatIAService.update_chat(db, chat_id, current_user.id, chat_data)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    return ChatIAService.serialize_chat_response(chat)

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Elimina un chat específico"""
    success = ChatIAService.delete_chat(db, chat_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Chat eliminado correctamente"}
    )

@router.delete("/")
async def clear_all_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Elimina todos los chats del usuario"""
    count = ChatIAService.clear_user_chats(db, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Se eliminaron {count} chats correctamente"}
    )

@router.get("/stats/summary")
async def get_chat_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene estadísticas de chats del usuario"""
    stats = ChatIAService.get_chat_statistics(db, current_user.id)
    return stats