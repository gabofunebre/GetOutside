# app/crud.py
import os
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from . import models, schemas

PDF_DIR = "app/static/catalogos"

# === PRODUCTOS ===
def get_producto(db: Session, codigo: str):
    return db.query(models.Producto).filter_by(codigo_getoutside=codigo).first()

def create_producto(db: Session, p: schemas.ProductoCreate):
    db_p = models.Producto(**p.dict())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p

def agregar_stock(db: Session, producto: models.Producto, stock_agregado: int):
    producto.stock_actual += stock_agregado
    db.commit()
    db.refresh(producto)
    return producto

# === STOCK / INVENTARIO ===
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

# === MÉTODOS DE PAGO ===
def create_payment_method(db: Session, pm: schemas.PaymentMethodCreate):
    # Verifica si ya existe un medio con el mismo nombre (case-insensitive)
    existente = db.query(models.PaymentMethod).filter(
        func.lower(models.PaymentMethod.name) == pm.name.lower()
    ).first()

    if existente:
        raise ValueError(f"Ya existe un medio de pago con el nombre '{pm.name}'.")

    pm_obj = models.PaymentMethod(name=pm.name)
    db.add(pm_obj)
    db.commit()
    db.refresh(pm_obj)
    return pm_obj

def get_payment_methods(db: Session):
    return db.query(models.PaymentMethod).all()

def delete_payment_method_by_id(db: Session, id: int) -> bool:
    usado = db.query(models.VentaPago).filter_by(payment_method_id=id).first()
    if usado:
        raise ValueError("No se puede eliminar: el medio fue utilizado en ventas.")

    pm = db.query(models.PaymentMethod).filter(models.PaymentMethod.id == id).first()
    if not pm:
        return False

    db.delete(pm)
    db.commit()
    return True

def update_payment_method_by_id(db: Session, id: int, new_name: str) -> models.PaymentMethod | None:
    pm = db.query(models.PaymentMethod).filter(models.PaymentMethod.id == id).first()
    if not pm:
        return None
    pm.name = new_name
    db.commit()
    db.refresh(pm)
    return pm

# === CATÁLOGOS ===
def create_catalogo(db: Session, file: UploadFile) -> models.Catalogo:
    existing = db.query(models.Catalogo).filter_by(filename=file.filename).first()
    if existing:
        raise ValueError(f"Ya existe un cat\u00e1logo con el nombre '{file.filename}'.")

    os.makedirs(PDF_DIR, exist_ok=True)
    dest_path = os.path.join(PDF_DIR, file.filename)
    with open(dest_path, "wb") as out:
        out.write(file.file.read())

    db_obj = models.Catalogo(filename=file.filename, filepath=dest_path)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_catalogos(db: Session):
    return db.query(models.Catalogo).order_by(models.Catalogo.uploaded_at.desc()).all()

def get_catalogo(db: Session, catalogo_id: int) -> Optional[models.Catalogo]:
    return db.query(models.Catalogo).filter(models.Catalogo.id == catalogo_id).first()

# === VENTAS Y PAGOS ===
def create_venta(db: Session, v: schemas.VentaCreate):
    total_detalles = sum(item.cantidad * item.precio_unitario for item in v.detalles)
    total_descuentos = sum(d.amount for d in v.descuentos or [])
    total_venta = total_detalles - total_descuentos
    total_pagos = sum(p.amount for p in v.pagos)

    if total_pagos != total_venta:
        raise ValueError("La suma de pagos debe coincidir con el total neto de la venta (con descuentos)")

    venta = models.Venta(total=total_venta)
    db.add(venta)
    db.flush()

    for item in v.detalles:
        prod = get_producto(db, item.codigo_getoutside)
        if prod.stock_actual < item.cantidad:
            raise ValueError(f"Sin stock: {item.codigo_getoutside}")
        db.add(models.DetalleVenta(
            venta_id=venta.id,
            codigo_getoutside=item.codigo_getoutside,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=item.cantidad * item.precio_unitario
        ))
        prod.stock_actual -= item.cantidad
        db.add(models.InventarioMovimiento(
            codigo_getoutside=item.codigo_getoutside,
            tipo=models.TipoMov.SALIDA,
            cantidad=item.cantidad,
            referencia=f"Venta #{venta.id}"
        ))

    for p in v.pagos:
        db.add(models.VentaPago(
            venta_id=venta.id,
            payment_method_id=p.payment_method_id,
            amount=p.amount
        ))

    for d in v.descuentos or []:
        db.add(models.Descuento(
            venta_id=venta.id,
            concepto=d.concepto,
            amount=d.amount
        ))

    db.commit()
    db.refresh(venta)
    return venta

# === CONSULTAS E INFORMES ===
def get_ingresos(db: Session):
    total = db.query(func.sum(models.VentaPago.amount)).scalar() or 0
    rows = (
        db.query(models.PaymentMethod.name, func.sum(models.VentaPago.amount))
        .join(models.VentaPago, models.PaymentMethod.id == models.VentaPago.payment_method_id)
        .group_by(models.PaymentMethod.name)
        .all()
    )
    return {"total": float(total), "por_medio": {name: float(amount) for name, amount in rows}}

def get_ventas(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    payment_method_id: Optional[int] = None,
    codigo_getoutside: Optional[str] = None,
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

    return query.options(
        joinedload(models.Venta.detalles).joinedload(models.DetalleVenta.producto),
        joinedload(models.Venta.pagos).joinedload(models.VentaPago.metodo)
    ).order_by(models.Venta.fecha.desc()).all()

def get_product_ranking(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    tipo: Optional[str] = None,
    proceso_aplicado: Optional[str] = None,
    diseno_aplicado: Optional[str] = None,
):
    query = db.query(
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
    ).join(models.DetalleVenta).join(models.Venta)

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

    return query.group_by(
        models.Producto.codigo_getoutside,
        models.Producto.codigo_mercaderia,
        models.Producto.tipo,
        models.Producto.color_prenda,
        models.Producto.proceso_aplicado,
        models.Producto.diseno_aplicado,
        models.Producto.variante_diseno,
        models.Producto.talle,
        models.Producto.precio_venta
    ).order_by(func.sum(models.DetalleVenta.cantidad).desc()).all()
