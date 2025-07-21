# app/routers/dashboard.py
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from app.core.templates import templates
from app.core.deps import get_db
from app.crud.users import get_user

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(request: Request, db: Session = Depends(get_db)):
    user = None
    photo_url = None
    user_id = request.session.get("user_id")
    if user_id:
        user = get_user(db, user_id)
        if user and user.foto_filename:
            photo_url = f"/static/uploads/usuarios/{user.id}/{user.foto_filename}"
    ctx = {"request": request, "user_photo": photo_url}
    return templates.TemplateResponse("dashboard.html", ctx)


@router.get("/admin", response_class=HTMLResponse)
def show_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@router.get("/consultas", response_class=HTMLResponse)
def show_consultas(request: Request):
    return templates.TemplateResponse("consultas.html", {"request": request})


@router.get("/metrics", response_class=HTMLResponse)
def show_metrics(request: Request):
    return templates.TemplateResponse("metrics.html", {"request": request})
