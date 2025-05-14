# app/crud.py
import os
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime
from fastapi import UploadFile
from . import models, schemas

PDF_DIR = "app/static/catalogos"

# -- Productos --
def get_producto(db: Session, codigo: str):
    return db.query(models.Producto).filter_by(codigo_getoutside=codigo).first()

def create_producto(db: Session, p: schemas.ProductoCreate):
    db_p = models.Producto(**p.dict())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p

# -- Stock / Movimientos --
def update_stock(db: Session, codigo: str, delta: int, referencia: str):
    prod = get_producto(db, codigo)
    prod.stock_actual += delta
    mov = models.InventarioMovimiento(
        codigo_getoutside=codigo,
        tipo=models.TipoMov.ENTRADA if delta > 0 else models.TipoMov.SALIDA,
        cantidad=abs(delta),
        referencia=referencia
    )
    db.add(mov)
    db.commit()
    return prod

# -- Ventas + Pagos --
def create_venta(db: Session, v: schemas.VentaCreate):
    total_detalles = sum(item.cantidad * item.precio_unitario for item in v.detalles)
    total_pagos = sum(p.amount for p in v.pagos)
    if total_pagos != total_detalles:
        raise ValueError("La suma de pagos debe coincidir con el total de la venta")

    venta = models.Venta(total=total_detalles)
    db.add(venta)
    db.flush()

    for item in v.detalles:
        prod = get_producto(db, item.codigo_getoutside)
        if prod.stock_actual < item.cantidad:
            raise ValueError(f"Sin stock: {item.codigo_getoutside}")
        dv = models.DetalleVenta(
            venta_id=venta.id,
            codigo_getoutside=item.codigo_getoutside,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=item.cantidad * item.precio_unitario
        )
        db.add(dv)
        prod.stock_actual -= item.cantidad
        mov = models.InventarioMovimiento(
            codigo_getoutside=item.codigo_getoutside,
            tipo=models.TipoMov.SALIDA,
            cantidad=item.cantidad,
            referencia=f"Venta #{venta.id}"
        )
        db.add(mov)

    for p in v.pagos:
        vp = models.VentaPago(
            venta_id=venta.id,
            payment_method_id=p.payment_method_id,
            amount=p.amount
        )
        db.add(vp)

    db.commit()
    db.refresh(venta)
    return venta

# -- INGRESOS (total y por método) --
def get_ingresos(db: Session):
    # Total recaudado
    total = db.query(func.sum(models.VentaPago.amount)).scalar() or 0
    # Desglose por método
    rows = (
        db.query(models.PaymentMethod.name, func.sum(models.VentaPago.amount))
          .join(models.VentaPago, models.PaymentMethod.id == models.VentaPago.payment_method_id)
          .group_by(models.PaymentMethod.name)
          .all()
    )
    por_medio = {name: float(amount) for name, amount in rows}
    return {"total": float(total), "por_medio": por_medio}

# -- Listar métodos de pago --
def create_payment_method(db: Session, pm: schemas.PaymentMethodCreate):
    pm_obj = models.PaymentMethod(name=pm.name)
    db.add(pm_obj)
    db.commit()
    db.refresh(pm_obj)
    return pm_obj

def get_payment_methods(db: Session):
    return db.query(models.PaymentMethod).all()

# -- Listar ventas para filtros --
def get_ventas(
    db: Session,
    start: datetime | None = None,
    end:   datetime | None = None,
    payment_method_id: int | None = None,
    codigo_getoutside: str | None = None,
):
    query = db.query(models.Venta)
    if start:
        query = query.filter(models.Venta.fecha >= start)
    if end:
        query = query.filter(models.Venta.fecha <= end)
    if payment_method_id:
        query = query.join(models.VentaPago).filter(models.VentaPago.payment_method_id == payment_method_id)
    if codigo_getoutside:
        query = query.join(models.DetalleVenta).filter(models.DetalleVenta.codigo_getoutside == codigo_getoutside)
    query = query.options(
        joinedload(models.Venta.detalles),
        joinedload(models.Venta.pagos).joinedload(models.VentaPago.metodo)
    )
    return query.order_by(models.Venta.fecha.desc()).all()

# -- Ranking de productos vendidos --
def get_product_ranking(
    db: Session,
    start: datetime | None = None,
    end:   datetime | None = None,
    tipo:               str | None = None,
    proceso_aplicado:   str | None = None,
    diseno_aplicado:    str | None = None,
):
    query = (
        db.query(
            models.Producto.codigo_getoutside,
            models.Producto.codigo_mercaderia,
            models.Producto.tipo,
            models.Producto.color_prenda,
            models.Producto.proceso_aplicado,
            models.Producto.diseno_aplicado,
            models.Producto.variante_diseno,
            models.Producto.talle,
            models.Producto.precio_venta,
            func.sum(models.DetalleVenta.cantidad).label("sold_qty")
        )
        .join(models.DetalleVenta, models.Producto.codigo_getoutside == models.DetalleVenta.codigo_getoutside)
        .join(models.Venta, models.DetalleVenta.venta_id == models.Venta.id)
    )
    if start:
        query = query.filter(models.Venta.fecha >= start)
    if end:
        query = query.filter(models.Venta.fecha <= end)
    if tipo:
        query = query.filter(models.Producto.tipo == tipo)
    if proceso_aplicado:
        query = query.filter(models.Producto.proceso_aplicado == proceso_aplicado)
    if diseno_aplicado:
        query = query.filter(models.Producto.diseno_aplicado == diseno_aplicado)

    query = query.group_by(
        models.Producto.codigo_getoutside,
        models.Producto.codigo_mercaderia,
        models.Producto.tipo,
        models.Producto.color_prenda,
        models.Producto.proceso_aplicado,
        models.Producto.diseno_aplicado,
        models.Producto.variante_diseno,
        models.Producto.talle,
        models.Producto.precio_venta,
    ).order_by(func.sum(models.DetalleVenta.cantidad).desc())

    return query.all()

def create_catalogo(db: Session, file: UploadFile) -> models.Catalogo:
    # Asegúrate de que exista la carpeta
    os.makedirs(PDF_DIR, exist_ok=True)
    dest_path = os.path.join(PDF_DIR, file.filename)
    with open(dest_path, "wb") as f:
        f.write(file.file.read())
    db_obj = models.Catalogo(
        filename=file.filename,
        filepath=f"/static/catalogos/{file.filename}"
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_catalogos(db: Session):
    return db.query(models.Catalogo).order_by(models.Catalogo.uploaded_at.desc()).all()

def get_catalogo(db: Session, catalogo_id: int) -> models.Catalogo | None:
    return db.query(models.Catalogo).filter(models.Catalogo.id == catalogo_id).first()

def create_catalogo(db: Session, file: UploadFile) -> models.Catalogo:
    # asegurarnos de que exista la carpeta
    os.makedirs(PDF_DIR, exist_ok=True)
    dest_path = os.path.join(PDF_DIR, file.filename)
    with open(dest_path, "wb") as out:
        out.write(file.file.read())
    db_obj = models.Catalogo(
        filename=file.filename,
        filepath=dest_path
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj