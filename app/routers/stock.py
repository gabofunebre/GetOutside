# app/routers/stock.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.templates import templates
from app.models import Producto

from app.core.deps import get_db

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("/", response_class=HTMLResponse)
def stock_overview(request: Request, db: Session = Depends(get_db)):
    productos = (
        db.query(Producto).order_by(Producto.codigo_getoutside).all()
    )
    return templates.TemplateResponse(
        "stock_overview.html", {"request": request, "productos": productos}
    )
