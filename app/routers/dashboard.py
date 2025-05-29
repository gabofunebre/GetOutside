# app/routers/dashboard.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def show_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
def show_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@router.get("/consultas", response_class=HTMLResponse)
def show_consultas(request: Request):
    return templates.TemplateResponse("consultas.html", {"request": request})


@router.get("/metrics", response_class=HTMLResponse)
def show_metrics(request: Request):
    return templates.TemplateResponse("metrics.html", {"request": request})
