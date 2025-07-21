from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette import status

from app.core.templates import templates
from app.core.deps import get_db
from app.crud.users import (
    create_user,
    authenticate_user,
    get_users,
    get_user,
    change_user_role,
    delete_user,
    update_user,
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
            {"request": request, "error": "Credenciales inválidas"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request.session["user_id"] = user.id
    request.session["role"] = user.role.value
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        create_user(db, email, password)
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/auth/google")
def google_auth_placeholder():
    """Placeholder for future Google OAuth2 implementation."""
    raise HTTPException(status_code=501, detail="Google OAuth no implementado")


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
    delete_user(db, user_id)
    return RedirectResponse("/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/config", response_class=HTMLResponse)
def user_config(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    user = get_user(db, user_id)
    return templates.TemplateResponse(
        "user_config.html", {"request": request, "user": user}
    )


@router.post("/config")
def user_config_post(
    request: Request,
    first_name: str = Form("") ,
    last_name: str = Form("") ,
    email: str = Form(...),
    password: str = Form(None),
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    try:
        update_user(db, user_id, first_name, last_name, email, password)
    except ValueError as e:
        user = get_user(db, user_id)
        return templates.TemplateResponse(
            "user_config.html",
            {"request": request, "user": user, "error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
