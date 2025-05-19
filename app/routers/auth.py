
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from database import get_db, User
from models.user import UserCreate, UserInDB, Token
from services.auth_service import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user, oauth2_scheme
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import RedirectResponse

from config import templates


router = APIRouter(tags=["autenticacion"])

@router.get("/login", response_class=HTMLResponse,
    summary="Página de inicio de sesión",
    description="Renderiza el formulario para que el usuario pueda iniciar sesión en la plataforma.")
async def login_page(request: Request):
    """Renderiza la página de inicio de sesión."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse,
    summary="Procesar inicio de sesión",
    description="Procesa el formulario de inicio de sesión y crea la cookie de autenticación si las credenciales son correctas.")
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Procesa el formulario de inicio de sesión."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña incorrectos"},
            status_code=401,
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=60*ACCESS_TOKEN_EXPIRE_MINUTES,
        samesite="lax"
    )
    return response

@router.post("/token", response_model=Token,
    summary="Obtener token de acceso",
    description="Devuelve un token JWT válido para autenticación usando OAuth2.")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=UserInDB,
    summary="Crear usuario",
    description="Crea un nuevo usuario en la base de datos.")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/me/", response_model=UserInDB,
    summary="Obtener usuario actual",
    description="Devuelve la información del usuario autenticado actual.")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users/", response_model=List[UserInDB],
    summary="Listar usuarios",
    description="Devuelve una lista de todos los usuarios (solo para técnicos).")
async def read_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Solo los técnicos pueden ver la lista de usuarios
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No tiene permisos para ver esta información")
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}", response_model=UserInDB,
    summary="Actualizar usuario",
    description="Actualiza los datos de un usuario existente")
async def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Solo los técnicos pueden editar usuarios
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No tiene permisos para editar usuarios")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Actualizar campos
    db_user.username = user.username
    db_user.email = user.email
    db_user.hashed_password = get_password_hash(user.password)
    db_user.role = user.role
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", status_code=204,    
    summary="Eliminar usuario",
    description="Elimina un usuario de la base de datos (solo para técnicos).")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), token: str = Depends(oauth2_scheme)):
    # Solo los técnicos pueden borrar usuarios
    if current_user.role != "tecnico":
        raise HTTPException(status_code=403, detail="No tiene permisos para borrar usuarios")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_user)
    db.commit()
    return

@router.get("/logout",
    summary="Cerrar sesión",
    description="Elimina la cookie de autenticación y redirige al login."
)
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/perfil", response_class=HTMLResponse, summary="Perfil del usuario")
async def perfil_usuario(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Muestra los atributos del usuario autenticado."""
    return templates.TemplateResponse(
        "perfil.html",
        {"request": request, "user": current_user}
    )

from fastapi import Form
from typing import Optional
from services.auth_service import get_password_hash, verify_password
@router.post("/perfil/actualizar", response_class=HTMLResponse)
async def actualizar_perfil(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    current_password: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None),
    confirm_password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualiza los datos del usuario autenticado."""
    # Verificar si el email o username ya están en uso por otro usuario
    if db.query(User).filter(User.email == email, User.id != current_user.id).first():
        return templates.TemplateResponse(
            "perfil.html",
            {"request": request, "user": current_user, "error": "El correo electrónico ya está en uso."}
        )
    if db.query(User).filter(User.username == username, User.id != current_user.id).first():
        return templates.TemplateResponse(
            "perfil.html",
            {"request": request, "user": current_user, "error": "El nombre de usuario ya está en uso."}
        )

    # Actualizar los datos básicos
    current_user.username = username
    current_user.email = email

    # Verificar si se desea cambiar la contraseña
    if current_password and new_password and confirm_password:
        if not verify_password(current_password, current_user.hashed_password):
            return templates.TemplateResponse(
                "perfil.html",
                {"request": request, "user": current_user, "error": "La contraseña actual es incorrecta."}
            )
        if new_password != confirm_password:
            return templates.TemplateResponse(
                "perfil.html",
                {"request": request, "user": current_user, "error": "Las contraseñas no coinciden."}
            )
        current_user.hashed_password = get_password_hash(new_password)

    # Guardar los cambios en la base de datos
    db.commit()
    db.refresh(current_user)

    return templates.TemplateResponse(
        "perfil.html",
        {"request": request, "user": current_user, "success": "Perfil actualizado correctamente."}
    )