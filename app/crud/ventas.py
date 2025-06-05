from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import (
    Venta,
    DetalleVenta,
    Descuento,
    VentaPago,
    PaymentMethod,
    Vuelto,
    MovimientoDinero,
    Producto,
    InventarioMovimiento,
    TipoMov,
    TipoMovimientoDinero,
)
from app.schemas.venta import VentaCreate
from app.core.currencies import CURRENCY_LABELS
from .inventario import get_producto


def create_venta(db: Session, v: VentaCreate) -> Venta:
    """Valida y registra una venta con sus detalles, pagos y descuentos."""
    total_detalles = sum(item.cantidad * item.precio_unitario for item in v.detalles)
    total_descuentos = sum(d.amount for d in v.descuentos or [])
    total_venta = total_detalles - total_descuentos

    venta = Venta(
        total=total_venta,
        fecha=v.fecha  # 👈 ahora se asume que siempre viene (requerido)
    )
    db.add(venta)
    db.flush()

    codigos: list[str] = []

    for item in v.detalles:
        prod = get_producto(db, item.producto_id)
        if not prod:
            raise ValueError(f"Producto con ID {item.producto_id} no encontrado")
        if prod.stock_actual < item.cantidad:
            raise ValueError(f"Sin stock: producto {item.producto_id}")

        db.add(
            DetalleVenta(
                venta_id=venta.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                subtotal=item.cantidad * item.precio_unitario,
            )
        )

        codigos.append(prod.codigo_getoutside)

        prod.stock_actual -= item.cantidad
        db.add(
            InventarioMovimiento(
                producto_id=item.producto_id,
                tipo=TipoMov.SALIDA,
                cantidad=item.cantidad,
                referencia=f"Venta #{venta.id}",
            )
        )

    codigos_str = " - ".join(codigos)

    for p in v.pagos:
        db.add(
            VentaPago(
                venta_id=venta.id,
                payment_method_id=p.payment_method_id,
                amount=p.amount,
            )
        )
        db.add(
            MovimientoDinero(
                tipo=TipoMovimientoDinero.INGRESO,
                fecha=v.fecha,
                concepto=f"V#{venta.id} - {codigos_str}",
                importe=p.amount,
                payment_method_id=p.payment_method_id,
            )
        )

    for d in v.descuentos or []:
        db.add(Descuento(
            venta_id=venta.id,
            concepto=d.concepto,
            amount=d.amount
        ))

    for ch in v.vueltos or []:
        db.add(
            Vuelto(
                venta_id=venta.id,
                payment_method_id=ch.payment_method_id,
                amount=ch.amount,
            )
        )

        db.add(
            MovimientoDinero(
                tipo=TipoMovimientoDinero.EGRESO,
                fecha=venta.fecha,
                concepto=f"Vuelto de venta #{venta.id}",
                importe=ch.amount,
                payment_method_id=ch.payment_method_id,
            )
        )

    db.commit()
    db.refresh(venta)
    return venta



def get_ventas(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    payment_method_id: Optional[int] = None,
    producto_ids: Optional[list[int]] = None,
) -> list[Venta]:
    """Recupera ventas con filtros opcionales de fecha, método y lista de productos."""
    query = db.query(Venta)

    if start:
        query = query.filter(Venta.fecha >= start)
    if end:
        # "end" se interpreta como fecha final inclusiva. Para incluir todo el
        # día se avanza un día y se filtra con '<'.
        end_plus_one = end + timedelta(days=1)
        query = query.filter(Venta.fecha < end_plus_one)
    if payment_method_id:
        query = query.join(VentaPago).filter(
            VentaPago.payment_method_id == payment_method_id
        )
    if producto_ids:
        query = query.join(DetalleVenta).filter(
            DetalleVenta.producto_id.in_(producto_ids)
        )

    return (
        query.options(
            joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
            joinedload(Venta.pagos).joinedload(VentaPago.metodo),
            joinedload(Venta.vueltos).joinedload(Vuelto.metodo),
        )
        .order_by(Venta.fecha.desc())
        .all()
    )


def get_product_ranking(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    tipo: Optional[str] = None,
    proceso_aplicado: Optional[str] = None,
    diseno_aplicado: Optional[str] = None,
) -> list:
    """Devuelve ranking de productos por cantidad vendida con filtros opcionales."""
    query = (
        db.query(
            Producto.id,
            Producto.codigo_getoutside,
            Producto.descripcion,
            func.sum(DetalleVenta.cantidad).label("sold_qty"),
        )
        .join(DetalleVenta)
        .join(Venta)
    )

    if start:
        query = query.filter(Venta.fecha >= start)
    if end:
        # Incluir el día "end" completo avanzando un día y usando '<'
        end_plus_one = end + timedelta(days=1)
        query = query.filter(Venta.fecha < end_plus_one)
    if tipo:
        query = query.filter(Producto.descripcion == tipo)
    if proceso_aplicado:
        query = query.filter(Producto.descripcion == proceso_aplicado)
    if diseno_aplicado:
        query = query.filter(Producto.descripcion == diseno_aplicado)

    return (
        query.group_by(Producto.id, Producto.codigo_getoutside, Producto.descripcion)
        .order_by(func.sum(DetalleVenta.cantidad).desc())
        .all()
    )


def filtrar_ventas(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    payment_method_id: Optional[int] = None,
    codigo_getoutside: Optional[str] = None,
) -> tuple[list[Venta], Optional[str]]:
    """
    Aplica filtros para buscar ventas y devuelve también el nombre del método de pago (si corresponde).
    """
    # Filtro por producto
    producto_ids = None
    if codigo_getoutside:
        productos = (
            db.query(Producto)
            .filter(Producto.codigo_getoutside.ilike(f"%{codigo_getoutside}%"))
            .all()
        )
        producto_ids = [p.id for p in productos] if productos else []

    # Obtener ventas con la función existente
    ventas = get_ventas(
        db=db,
        start=start,
        end=end,
        payment_method_id=payment_method_id,
        producto_ids=producto_ids,
    )

    # Buscar nombre del método de pago (si se aplicó filtro)
    metodo_pago_nombre = None
    if payment_method_id and ventas:
        for v in ventas:
            for p in v.pagos:
                if p.payment_method_id == payment_method_id:
                    metodo_pago_nombre = p.metodo.name
                    break
            if metodo_pago_nombre:
                break

    return ventas, metodo_pago_nombre


def get_venta_by_id(db: Session, venta_id: int) -> Venta | None:
    """
    Devuelve una venta con todos sus detalles, pagos y descuentos cargados.
    """
    return (
        db.query(Venta)
        .options(
            joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
            joinedload(Venta.pagos).joinedload(VentaPago.metodo),
            joinedload(Venta.descuentos),
            joinedload(Venta.vueltos).joinedload(Vuelto.metodo),
        )
        .filter(Venta.id == venta_id)
        .first()
    )
