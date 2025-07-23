import os
import secrets
from urllib.parse import urlencode
import requests
from fastapi import APIRouter, Depends, Form, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.status import HTTP_302_FOUND

from app.core.templates import templates
from app.core.deps import get_db
from app.crud.users import (
    create_user,
    authenticate_user,
    get_user_by_email,
    get_users,
    get_user,
    change_user_role,
    delete_user,
    update_user,
    save_remote_photo,
)
from app.models.user import UserRole

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Credenciales inválidas",
                "email": email,
                "password": password,
            },
            status_code=400,
        )

    # Modificá la sesión
    request.session["user_id"] = user.id
    request.session["role"] = user.role.value

    #LOG DE DEBUG
    print("🔐 Session set:", dict(request.session))


    # Redirección explícita
    response = RedirectResponse("/", status_code=HTTP_302_FOUND)
    return response


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register_action(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
):
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Las contrase\xC3\xB1as no coinciden"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = create_user(
            db,
            email,
            password,
            first_name=first_name,
            last_name=last_name,
            oauth_provider="local",
        )
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request.session["user_id"] = user.id
    request.session["role"] = user.role.value
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/auth/google")
def google_auth(request: Request):
    """Inicio del flujo OAuth con Google."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for("google_auth_callback")
    if not client_id:
        raise HTTPException(status_code=500, detail="Google OAuth no configurado")
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(url)


@router.get("/auth/google/callback")
def google_auth_callback(request: Request, code: str = None, state: str = None, db: Session = Depends(get_db)):
    if not code or not state:
        raise HTTPException(status_code=400, detail="Código o estado faltante")
    if state != request.session.pop("oauth_state", None):
        raise HTTPException(status_code=400, detail="Estado inválido")

    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for("google_auth_callback")
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        headers={"Accept": "application/json"},
    )
    if not token_resp.ok:
        raise HTTPException(status_code=400, detail="Error obteniendo token de Google")

    access_token = token_resp.json().get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Token no recibido")

    userinfo_resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not userinfo_resp.ok:
        raise HTTPException(status_code=400, detail="Error consultando usuario")

    profile = userinfo_resp.json()
    email = profile.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email no disponible")

    first_name = profile.get("given_name", "")
    last_name = profile.get("family_name", "")

    user = get_user_by_email(db, email)
    if not user:
        random_password = secrets.token_urlsafe(16)
        user = create_user(
            db,
            email,
            random_password,
            first_name=first_name,
            last_name=last_name,
            oauth_provider="google",
        )

    picture = profile.get("picture")
    if picture and not user.foto_filename:
        filename = save_remote_photo(user.id, picture)
        if filename:
            user.foto_filename = filename
            db.commit()

    request.session["user_id"] = user.id
    request.session["role"] = user.role.value
    return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)


@router.post("/config/delete")
def delete_own_account(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    success = delete_user(db, user_id)
    if not success:
        user = get_user(db, user_id)
        return templates.TemplateResponse(
            "user_config.html",
            {
                "request": request,
                "user": user,
                "google_user": user.oauth_provider == "google",
                "error": "La cuenta administradora no puede eliminarse",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.get("/admin/users", response_class=HTMLResponse)
def manage_users(request: Request, db: Session = Depends(get_db)):
    users = get_users(db)
    return templates.TemplateResponse(
        "manage_users.html", {"request": request, "users": users, "roles": list(UserRole)}
    )


@router.post("/admin/users/change")
def change_role(
    user_id: int = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
):
    change_user_role(db, user_id, UserRole(role))
    return RedirectResponse("/admin/users", status_code=status.HTTP_302_FOUND)


@router.post("/admin/users/delete")
def delete_user_action(user_id: int = Form(...), db: Session = Depends(get_db)):
    success = delete_user(db, user_id)
    return RedirectResponse("/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/config", response_class=HTMLResponse)
def user_config(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    user = get_user(db, user_id)
    return templates.TemplateResponse(
        "user_config.html",
        {"request": request, "user": user, "google_user": user.oauth_provider == "google"},
    )


@router.post("/config")
def user_config_post(
    request: Request,
    first_name: str = Form("") ,
    last_name: str = Form("") ,
    email: str = Form(...),
    password: str = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    user = get_user(db, user_id)
    try:
        if user.oauth_provider == "google":
            update_user(db, user_id, user.first_name or "", user.last_name or "", user.email, None, foto)
        else:
            update_user(db, user_id, first_name, last_name, email, password, foto)
    except ValueError as e:
        return templates.TemplateResponse(
            "user_config.html",
            {
                "request": request,
                "user": user,
                "google_user": user.oauth_provider == "google",
                "error": str(e),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
