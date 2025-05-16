# app/routers/ventas.py

from fastapi import (
    APIRouter, Depends, HTTPException, Request, Query
)
from fastapi.responses import HTMLResponse
from ..core.templates import templates
from sqlalchemy.orm import Session
from datetime import datetime
from .. import crud, schemas, database, models

router = APIRouter(prefix="/ventas", tags=["Ventas"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1) Formulario de registro de venta
@router.get("/new", response_class=HTMLResponse)
def new_sale_form(request: Request, db: Session = Depends(get_db)):
    productos_raw = db.query(models.Producto).all()
    medios_raw    = db.query(models.PaymentMethod).all()

    productos = [
        {
            "codigo_getoutside": p.codigo_getoutside,
            "descripcion":       p.descripcion,
            "precio_venta":      float(p.precio_venta),
        }
        for p in productos_raw
    ]
    medios = [
        {
            "id":   m.id,
            "name": m.name,
        }
        for m in medios_raw
    ]

    return templates.TemplateResponse(
        "sales_form.html",
        {
            "request": request,
            "productos": productos,
            "medios": medios
        }
    )

# 2) Pantalla de filtros
@router.get("/", response_class=HTMLResponse)
def ventas_filter(request: Request, db: Session = Depends(get_db)):
    medios = db.query(models.PaymentMethod).all()
    return templates.TemplateResponse(
        "ventas_filter.html",
        {"request": request, "payment_methods": medios}
    )

# 3) Listado de ventas según filtros
@router.get("/list", response_class=HTMLResponse)
def ventas_list(
    request: Request,
    start: str | None = Query(None),
    end:   str | None = Query(None),
    payment_method_id: str | None = Query(None),  # <- como str para control manual
    codigo_getoutside: str | None = Query(None),
    db: Session = Depends(get_db)
):
    start_dt = datetime.fromisoformat(start) if start and start.strip() else None
    end_dt   = datetime.fromisoformat(end)   if end and end.strip() else None
    metodo_id = int(payment_method_id) if payment_method_id and payment_method_id.strip().isdigit() else None
    codigo = codigo_getoutside.strip() if codigo_getoutside and codigo_getoutside.strip() else None

    ventas = crud.get_ventas(
        db,
        start=start_dt,
        end=end_dt,
        payment_method_id=metodo_id,
        codigo_getoutside=codigo
    )

    metodo_pago_nombre = None
    if metodo_id and ventas:
        for v in ventas:
            for p in v.pagos:
                if p.payment_method_id == metodo_id:
                    metodo_pago_nombre = p.metodo.name
                    break
            if metodo_pago_nombre:
                break

    return templates.TemplateResponse(
        "ventas_list.html",
        {
            "request": request,
            "ventas": ventas,
            "start": start,
            "end": end,
            "payment_method_id": metodo_id,
            "codigo_getoutside": codigo,
            "metodo_pago_nombre": metodo_pago_nombre
        }
    )


# 4) API JSON para crear venta
@router.post("/", response_model=schemas.VentaOut)
def create_venta_api(v: schemas.VentaCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_venta(db, v)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 5) API JSON para ingresos
@router.get("/ingresos")
def ingresos(db: Session = Depends(get_db)):
    return crud.get_ingresos(db)
