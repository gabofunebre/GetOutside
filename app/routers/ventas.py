# app/routers/ventas.py

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload

from .. import crud, schemas, database, models
from ..core.templates import templates

router = APIRouter(prefix="/ventas", tags=["Ventas"])

# === DEPENDENCIA: Sesión de base de datos ===

def get_db():
    """Proporciona una sesión de DB y la cierra al finalizar"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === 1) Formulario HTML para nueva venta ===
@router.get("/new", response_class=HTMLResponse)
def new_sale_form(request: Request, db: Session = Depends(get_db)):
    """Renderiza el formulario con productos y métodos de pago disponibles"""
    productos_raw = db.query(models.Producto).all()
    productos = [schemas.ProductoOut.from_orm(p).model_dump() for p in productos_raw]

    medios_raw = db.query(models.PaymentMethod).all()
    from ..core.currencies import CURRENCY_LABELS
    medios = [
        {
            "id": m.id,
            "name": m.name,
            "currency": m.currency,
            "currency_label": CURRENCY_LABELS.get(m.currency, m.currency)
        }
        for m in medios_raw
    ]
    return templates.TemplateResponse(
        "sales_form.html",
        {"request": request, "productos": productos, "medios": medios}
    )

# === 2) Pantalla de filtros para listar ventas ===
@router.get("/", response_class=HTMLResponse)
def ventas_filter(request: Request, db: Session = Depends(get_db)):
    """Muestra la página con filtros (fecha, método, producto)"""
    payment_methods = db.query(models.PaymentMethod).all()
    return templates.TemplateResponse(
        "ventas_filter.html",
        {"request": request, "payment_methods": payment_methods}
    )

# === 3) Listado de ventas según filtros ===
@router.get("/list", response_class=HTMLResponse)
def ventas_list(
    request: Request,
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    payment_method_id: Optional[str] = Query(None),
    codigo_getoutside: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Aplica filtros y renderiza la lista de ventas"""
    # Parsear fechas y IDs
    start_dt = datetime.fromisoformat(start) if start and start.strip() else None
    end_dt   = datetime.fromisoformat(end)   if end and end.strip() else None
    metodo_id = int(payment_method_id) if payment_method_id and payment_method_id.isdigit() else None

    # Obtener lista de productos si se aplica filtro por código
    producto_ids = None
    if codigo_getoutside:
        productos = db.query(models.Producto).filter(models.Producto.codigo_getoutside.ilike(f"%{codigo_getoutside}%")).all()
        producto_ids = [p.id for p in productos] if productos else []

    # Obtener ventas con crud.get_ventas
    ventas = crud.get_ventas(
        db,
        start=start_dt,
        end=end_dt,
        payment_method_id=metodo_id,
        producto_ids=producto_ids
    )

    # Obtener nombre del medio filtrado
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
            "codigo_getoutside": codigo_getoutside,
            "metodo_pago_nombre": metodo_pago_nombre
        }
    )
    
# === 4) API JSON para crear una venta ===
@router.post("/", response_model=schemas.VentaOut)
def create_venta_api(v: schemas.VentaCreate, db: Session = Depends(get_db)):
    """Registra una venta junto con detalles, pagos y descuentos"""
    try:
        return crud.create_venta(db, v)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# === 5) API JSON para obtener ingresos ===
@router.get("/ingresos")
def ingresos_api(db: Session = Depends(get_db)):
    """Devuelve total e ingresos por medio de pago"""
    return crud.get_ingresos(db)

# === 6) Detalle de una venta por ID ===
@router.get("/{venta_id}", response_class=HTMLResponse)
def detalle_venta(venta_id: int, request: Request, db: Session = Depends(get_db)):
    """Muestra la información completa de una venta específica"""
    venta = db.query(models.Venta).options(
        joinedload(models.Venta.detalles).joinedload(models.DetalleVenta.producto),
        joinedload(models.Venta.pagos).joinedload(models.VentaPago.metodo),
        joinedload(models.Venta.descuentos)
    ).filter(models.Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    return templates.TemplateResponse(
        "venta_detalle.html",
        {"request": request, "venta": venta}
    )
