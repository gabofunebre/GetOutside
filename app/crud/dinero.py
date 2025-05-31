# app/crud/dinero.py

from datetime import datetime
from sqlalchemy import func, case
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.models.enums import TipoMovimientoDinero
from app.models.dinero import MovimientoDinero, TenenciaAcumulada
from app.models.ventas import PaymentMethod
from app.core.currencies import get_exchange_rates, CURRENCY_LABELS
from app.core.config import DEFAULT_MOVIMIENTOS_LIMIT
from app.exceptions.dinero import MovimientoNoRegistrado, ConversionMonedaFallida, ConsultaTenenciasFallida, ActualizacionTenenciasFallida, MovimientoInvalido


# --- Crear / Guardar ---

def crear_movimiento(
    tipo: TipoMovimientoDinero,
    fecha: datetime,
    concepto: str,
    importe: float,
    metodo_pago_id: int,
) -> MovimientoDinero:
    """Crea un objeto MovimientoDinero validado. Lanza MovimientoInvalido si falla."""
    try:
        return MovimientoDinero(
            tipo=tipo,
            fecha=fecha,
            concepto=concepto,
            importe=importe,
            payment_method_id=metodo_pago_id,
        )
    except (TypeError, ValueError) as e:
        raise MovimientoInvalido(f"No se pudo crear MovimientoDinero: {e}") from e

def guardar_movimiento(db: Session, movimiento: MovimientoDinero) -> MovimientoDinero:
    """Guarda un objeto MovimientoDinero en la base de datos."""
    try:
        db.add(movimiento)
        db.commit()
        db.refresh(movimiento)
        return movimiento
    except SQLAlchemyError as e:
        db.rollback()
        raise MovimientoNoRegistrado("Error al guardar el movimiento.") from e

def crear_y_guardar_movimiento(
    db: Session,
    tipo: TipoMovimientoDinero,
    fecha: datetime,
    concepto: str,
    importe: float,
    metodo_pago_id: int,
) -> MovimientoDinero:
    """Crea y guarda un movimiento de dinero en una sola operación."""
    movimiento = crear_movimiento(
        tipo=tipo,
        fecha=fecha,
        concepto=concepto,
        importe=importe,
        metodo_pago_id=metodo_pago_id,
    )
    return guardar_movimiento(db, movimiento)


# --- Consultas / Lectura ---

def listar_movimientos(db: Session, limit: int = DEFAULT_MOVIMIENTOS_LIMIT):
    """
    Devuelve los últimos movimientos con su método de pago relacionado.
    """
    return (
        db.query(MovimientoDinero)
        .options(joinedload(MovimientoDinero.metodo_pago))
        .order_by(MovimientoDinero.fecha.desc())
        .limit(limit)
        .all()
    )

def get_movimiento_by_id(db: Session, movimiento_id: int) -> MovimientoDinero:
    """
    Devuelve un movimiento de dinero por su ID, incluyendo su método de pago.
    Lanza MovimientoNoRegistrado si no se encuentra.
    """
    movimiento = (
        db.query(MovimientoDinero)
        .options(joinedload(MovimientoDinero.metodo_pago))
        .filter(MovimientoDinero.id == movimiento_id)
        .first()
    )

    if not movimiento:
        raise MovimientoNoRegistrado(f"Movimiento con ID {movimiento_id} no encontrado.")

    return movimiento
