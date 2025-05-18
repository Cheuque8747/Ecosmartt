from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import templates
from services.deepseek_service import DeepSeekService

router = APIRouter(prefix="/ia", tags=["IA"])


@router.get("/chat", response_class=HTMLResponse)
async def ia_chat_page(request: Request):
    return templates.TemplateResponse("ia_chat.html", {"request": request})

@router.post("/chat")
async def ia_chat_api(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    deepseek = DeepSeekService()
    respuesta = deepseek.chat(messages)
    return respuesta