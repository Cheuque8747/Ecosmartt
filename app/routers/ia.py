from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import templates
from services.deepseek_service import DeepSeekService
from services.auth_service import get_current_active_user
from database import User
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/ia", tags=["IA"])


@router.get("/chat", response_class=HTMLResponse)
async def ia_chat_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "ia_chat.html",
        {"request": request, "user": current_user}
    )

@router.post("/chat")
async def ia_chat_api(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    deepseek = DeepSeekService()
    respuesta = deepseek.chat(messages)
    return respuesta