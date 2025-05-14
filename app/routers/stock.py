# app/routers/stock.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from ..core.templates import templates
from sqlalchemy.orm import Session
from .. import database, models

router = APIRouter(prefix="/stock", tags=["Stock"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def stock_overview(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).order_by(models.Producto.codigo_getoutside).all()
    return templates.TemplateResponse(
        "stock_overview.html",
        {"request": request, "productos": productos}
    )
