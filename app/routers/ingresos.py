# app/routers/ingresos.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from ..core.templates import templates
from sqlalchemy.orm import Session
from .. import database, crud

router = APIRouter(prefix="/ingresos", tags=["Ingresos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def ingresos_overview(request: Request, db: Session = Depends(get_db)):
    data = crud.get_ingresos(db)
    total = data["total"]
    por_medio = data["por_medio"]
    return templates.TemplateResponse(
        "ingresos_overview.html",
        {"request": request, "total": total, "por_medio": por_medio}
    )
