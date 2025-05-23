# app/routers/catalogos.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .. import database, models, schemas
from ..core.templates import templates

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])

# === Dependencia para obtener la sesión de base de datos ===

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === VISTA HTML DE CATÁLOGOS (PDFs) ===

@router.get("/", response_class=HTMLResponse)
def catalogos_html(request: Request, db: Session = Depends(get_db)):
    """Vista HTML con links a catálogos PDF"""
    catalogos = db.query(models.Catalogo).order_by(models.Catalogo.uploaded_at.desc()).all()
    return templates.TemplateResponse("catalogos.html", {"request": request, "catalogos": catalogos})


# === API JSON PARA FRONTEND ===

@router.get("/api", response_model=list[schemas.CatalogoOut])
def catalogos_json(db: Session = Depends(get_db)):
    """
    Endpoint JSON para el frontend.
    Devuelve todos los catálogos con ID y filename.
    """
    return db.query(models.Catalogo).all()
