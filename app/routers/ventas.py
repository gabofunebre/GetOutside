# app/routers/ventas.py

from datetime import datetime
#from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session #, joinedload

from app.core.templates import templates
from app.core.deps import get_db
from app.crud.ventas import create_venta, get_ventas, filtrar_ventas, get_venta_by_id
from app.crud.actions import log_action
from app.crud.tenencias import get_tenencias, get_tenencias_convertidas
from app.schemas.producto import ProductoOut
from app.schemas.venta import VentaCreate, VentaOut, VentaFilterParams
from app.models.ventas import Venta, DetalleVenta
from app.models.inventario import Producto
from app.models.ventas import PaymentMethod
from app.core.currencies import CURRENCY_LABELS

router = APIRouter(prefix="/ventas", tags=["Ventas"])


# === 1) Formulario HTML para nueva venta ===
@router.get("/new", response_class=HTMLResponse)
def new_sale_form(request: Request, db: Session = Depends(get_db)):
    """Renderiza el formulario con productos y métodos de pago disponibles"""
    productos_raw = db.query(Producto).all()
    productos = [ProductoOut.from_orm(p).model_dump() for p in productos_raw]

    medios_raw = db.query(PaymentMethod).all()

    medios = [
        {
            "id": m.id,
            "name": m.name,
            "currency": m.currency,
            "currency_label": CURRENCY_LABELS.get(m.currency, m.currency),
        }
        for m in medios_raw
    ]
    return templates.TemplateResponse(
        "sales_form.html",
        {"request": request, "productos": productos, "medios": medios},
    )


# === 2) Pantalla de filtros para listar ventas ===
@router.get("/", response_class=HTMLResponse)
def ventas_filter(request: Request, db: Session = Depends(get_db)):
    """Muestra la página con filtros (fecha, método, producto)"""
    payment_methods = db.query(PaymentMethod).all()
    return templates.TemplateResponse(
        "ventas_filter.html", {"request": request, "payment_methods": payment_methods}
    )


# === 3) Listado de ventas según filtros ===
@router.get("/list", response_class=HTMLResponse)
def ventas_list(
    request: Request,
    filtros: VentaFilterParams = Depends(),
    db: Session = Depends(get_db),
):
    """Aplica filtros y renderiza la lista de ventas"""

    start_dt = (
        datetime.fromisoformat(filtros.start)
        if filtros.start and filtros.start.strip()
        else None
    )
    end_dt = (
        datetime.fromisoformat(filtros.end)
        if filtros.end and filtros.end.strip()
        else None
    )
    metodo_id = (
        int(filtros.payment_method_id)
        if filtros.payment_method_id and filtros.payment_method_id.isdigit()
        else None
    )
    ventas, metodo_pago_nombre = filtrar_ventas(
        db=db,
        start=start_dt,
        end=end_dt,
        payment_method_id=metodo_id,
        codigo_getoutside=filtros.codigo_getoutside,
    )

    return templates.TemplateResponse(
        "ventas_list.html",
        {
            "request": request,
            "ventas": ventas,
            "start": filtros.start,
            "end": filtros.end,
            "payment_method_id": metodo_id,
            "codigo_getoutside": filtros.codigo_getoutside,
            "metodo_pago_nombre": metodo_pago_nombre,
        },
    )


# === 4) API JSON para crear una venta ===
@router.post("/", response_model=VentaOut)
def create_venta_api(v: VentaCreate, request: Request, db: Session = Depends(get_db)):
    """Registra una venta junto con detalles, pagos y descuentos"""
    try:
        venta = create_venta(db, v)
        user_id = request.session.get("user_id")
        if user_id:
            log_action(
                db,
                user_id=user_id,
                action="CREAR_VENTA",
                entity_type="VENTA",
                entity_id=venta.id,
                detail=f"Venta #{venta.id} registrada",
            )
        return venta
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# === 5) API JSON para obtener ingresos ===
@router.get("/ingresos")
def ingresos_api(db: Session = Depends(get_db)):
    """Devuelve total e ingresos por medio de pago"""
    return get_ingresos(db)


# === 6) Detalle de una venta por ID ===
@router.get("/{venta_id}", response_class=HTMLResponse)
def detalle_venta(venta_id: int, request: Request, db: Session = Depends(get_db)):
    """Muestra la información completa de una venta específica"""
    venta = get_venta_by_id(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    return templates.TemplateResponse(
        "venta_detalle.html", {"request": request, "venta": venta}
    )
