import os
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from . import models, schemas
from .core.currencies import CURRENCY_LABELS

PDF_DIR = "app/static/catalogos"

# === PRODUCTOS ===

def get_producto(db: Session, producto_id: int) -> Optional[models.Producto]:
    """Devuelve un Producto por su ID."""
    return db.query(models.Producto).filter(models.Producto.id == producto_id).first()

def create_producto(db: Session, p: schemas.ProductoCreate) -> models.Producto:
    """Crea y devuelve un nuevo Producto."""
    db_p = models.Producto(**p.dict())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p

def agregar_stock(db: Session, producto: models.Producto, stock_agregado: int) -> models.Producto:
    """Aumenta el stock_actual de un Producto existente."""
    producto.stock_actual += stock_agregado
    db.commit()
    db.refresh(producto)
    return producto


def update_producto_completo(db: Session, producto_id: int, data: schemas.ProductoCreate) -> models.Producto:
    """
    Actualiza completamente un producto existente:
    - Cambia código, descripción, precio, stock y catálogo.
    - Valida que el nuevo código no esté en uso por otro producto.
    """
    # Buscar producto por ID
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not prod:
        raise ValueError("Producto no encontrado")

    # Validar unicidad del código GetOutside, excluyendo el mismo producto
    duplicado = db.query(models.Producto).filter(
        models.Producto.codigo_getoutside == data.codigo_getoutside,
        models.Producto.id != producto_id
    ).first()
    if duplicado:
        raise ValueError("Código GetOutside ya en uso por otro producto.")

    # Asignar nuevos valores
    prod.codigo_getoutside = data.codigo_getoutside
    prod.descripcion = data.descripcion
    prod.precio_venta = data.precio_venta
    prod.stock_actual = data.stock_actual
    prod.catalogo_id = data.catalogo_id

    # Guardar cambios
    db.commit()
    db.refresh(prod)

    return prod

# === STOCK / INVENTARIO ===

def update_stock(db: Session, producto_id: int, delta: int, referencia: str) -> models.Producto:
    """Crea un movimiento de inventario y ajusta el stock del Producto."""
    prod = get_producto(db, producto_id)
    prod.stock_actual += delta
    mov = models.InventarioMovimiento(
        producto_id=producto_id,
        tipo=models.TipoMov.ENTRADA if delta > 0 else models.TipoMov.SALIDA,
        cantidad=abs(delta),
        referencia=referencia
    )
    db.add(mov)
    db.commit()
    return prod

# === MÉTODOS DE PAGO ===

def create_payment_method(db: Session, pm: schemas.PaymentMethodCreate):
    """Crea un nuevo medio de pago validando unicidad (case-insensitive)."""
    existente = db.query(models.PaymentMethod).filter(
        func.lower(models.PaymentMethod.name) == pm.name.lower()
    ).first()

    if existente:
        raise ValueError(f"Ya existe un medio de pago con el nombre '{pm.name}'.")

    pm_obj = models.PaymentMethod(
        name=pm.name,
        currency=pm.currency.upper()
    )
    db.add(pm_obj)
    db.commit()
    db.refresh(pm_obj)
    return pm_obj

def get_payment_methods(db: Session):
    """Recupera todos los métodos de pago registrados."""
    return db.query(models.PaymentMethod).all()

def delete_payment_method_by_id(db: Session, id: int) -> bool:
    """Elimina un método si no está referenciado en ventas."""
    usado = db.query(models.VentaPago).filter_by(payment_method_id=id).first()
    if usado:
        raise ValueError("No se puede eliminar: el medio fue utilizado en ventas.")

    pm = db.query(models.PaymentMethod).filter(models.PaymentMethod.id == id).first()
    if not pm:
        return False

    db.delete(pm)
    db.commit()
    return True

def update_payment_method_by_id(
    db: Session,
    id: int,
    new_name: str,
    new_currency: str
) -> models.PaymentMethod | None:
    """Actualiza nombre y moneda de un método de pago, validando unicidad."""
    pm = db.query(models.PaymentMethod).filter(models.PaymentMethod.id == id).first()
    if not pm:
        return None

    existente = db.query(models.PaymentMethod).filter(
        func.lower(models.PaymentMethod.name) == new_name.lower(),
        models.PaymentMethod.id != id
    ).first()
    if existente:
        raise ValueError(f"Ya existe un medio de pago con el nombre '{new_name}'.")

    pm.name = new_name
    pm.currency = new_currency.upper()
    db.commit()
    db.refresh(pm)
    return pm

# === CATÁLOGOS ===

def create_catalogo(db: Session, file: UploadFile) -> models.Catalogo:
    """Guarda un archivo PDF y registra un nuevo catálogo."""
    existing = db.query(models.Catalogo).filter_by(filename=file.filename).first()
    if existing:
        raise ValueError(f"Ya existe un catálogo con el nombre '{file.filename}'.")
    os.makedirs(PDF_DIR, exist_ok=True)
    dest_path = os.path.join(PDF_DIR, file.filename)
    with open(dest_path, "wb") as out:
        out.write(file.file.read())
    db_obj = models.Catalogo(filename=file.filename, filepath=dest_path)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_catalogos(db: Session) -> list[models.Catalogo]:
    """Recupera todos los catálogos ordenados por fecha descendente."""
    return db.query(models.Catalogo).order_by(models.Catalogo.uploaded_at.desc()).all()

def get_catalogo(db: Session, catalogo_id: int) -> Optional[models.Catalogo]:
    """Recupera un catálogo por su ID."""
    return db.query(models.Catalogo).filter(models.Catalogo.id == catalogo_id).first()

# === VENTAS Y PAGOS ===

def create_venta(db: Session, v: schemas.VentaCreate) -> models.Venta:
    """Valida y registra una venta con sus detalles, pagos y descuentos."""
    total_detalles = sum(item.cantidad * item.precio_unitario for item in v.detalles)
    total_descuentos = sum(d.amount for d in v.descuentos or [])
    total_venta = total_detalles - total_descuentos
    # Ya no se valida que total_pagos == total_venta
    venta = models.Venta(total=total_venta)
    db.add(venta)
    db.flush()
    for item in v.detalles:
        prod = get_producto(db, item.producto_id)
        if prod.stock_actual < item.cantidad:
            raise ValueError(f"Sin stock: producto {item.producto_id}")
        db.add(models.DetalleVenta(
            venta_id=venta.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=item.cantidad * item.precio_unitario
        ))
        prod.stock_actual -= item.cantidad
        db.add(models.InventarioMovimiento(
            producto_id=item.producto_id,
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

def get_ingresos(db: Session):
    """
    Devuelve ingresos agrupados por medio de pago con:
    - total: suma total de pagos
    - por_medio: lista de dicts con id, name, currency, currency_label y amount
    """
    total = db.query(func.sum(models.VentaPago.amount)).scalar() or 0

    rows = (
        db.query(
            models.PaymentMethod.id,
            models.PaymentMethod.name,
            models.PaymentMethod.currency,
            func.sum(models.VentaPago.amount).label("amount")
        )
        .join(models.VentaPago, models.PaymentMethod.id == models.VentaPago.payment_method_id)
        .group_by(
            models.PaymentMethod.id,
            models.PaymentMethod.name,
            models.PaymentMethod.currency
        )
        .all()
    )

    por_medio = [
        {
            "id": pm_id,
            "name": name,
            "currency": currency,
            "currency_label": CURRENCY_LABELS.get(currency, currency),
            "amount": float(amount)
        }
        for pm_id, name, currency, amount in rows
    ]

    return {"total": float(total), "por_medio": por_medio}

def get_ventas(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    payment_method_id: Optional[int] = None,
    producto_id: Optional[int] = None,
) -> list[models.Venta]:
    """Recupera ventas con filtros opcionales de fecha, método y producto."""
    query = db.query(models.Venta)
    if start:
        query = query.filter(models.Venta.fecha >= start)
    if end:
        query = query.filter(models.Venta.fecha <= end)
    if payment_method_id:
        query = query.join(models.VentaPago).filter(models.VentaPago.payment_method_id == payment_method_id)
    if producto_id:
        query = query.join(models.DetalleVenta).filter(models.DetalleVenta.producto_id == producto_id)
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
) -> list:
    """Devuelve ranking de productos por cantidad vendida con filtros opcionales."""
    query = db.query(
        models.Producto.id,
        models.Producto.codigo_getoutside,
        models.Producto.descripcion,
        func.sum(models.DetalleVenta.cantidad).label("sold_qty")
    ).join(models.DetalleVenta).join(models.Venta)
    if start:
        query = query.filter(models.Venta.fecha >= start)
    if end:
        query = query.filter(models.Venta.fecha <= end)
    if tipo:
        query = query.filter(models.Producto.descripcion == tipo)
    if proceso_aplicado:
        query = query.filter(models.Producto.descripcion == proceso_aplicado)
    if diseno_aplicado:
        query = query.filter(models.Producto.descripcion == diseno_aplicado)
    return query.group_by(
        models.Producto.id,
        models.Producto.codigo_getoutside,
        models.Producto.descripcion
    ).order_by(func.sum(models.DetalleVenta.cantidad).desc()).all()
