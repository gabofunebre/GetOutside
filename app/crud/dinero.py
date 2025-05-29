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
from app.exceptions.dinero import MovimientoNoRegistrado, ConversionMonedaFallida, ConsultaTenenciasFallida, ActualizacionTenenciasFallida


# --- Crear / Guardar ---

def crear_movimiento(
    tipo: TipoMovimientoDinero,
    fecha: datetime,
    concepto: str,
    importe: float,
    metodo_pago_id: int,
) -> MovimientoDinero:
    """Crea un objeto MovimientoDinero sin persistirlo en la base de datos."""
    return MovimientoDinero(
        tipo=tipo,
        fecha=fecha,
        concepto=concepto,
        importe=importe,
        payment_method_id=metodo_pago_id,
    )

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


# --- TENENCIAS / CONVERSIONES ---

def leer_tenencias_acumuladas(db: Session) -> list[TenenciaAcumulada]:
    try:
        return db.query(TenenciaAcumulada).all()
    except SQLAlchemyError as e:
        raise ConsultaTenenciasFallida("Error al leer tenencias acumuladas.") from e

def upsert_tenencia_acumulada(
    db: Session,
    payment_method_id: int,
    importe_acumulado: float,
    fecha_corte: datetime | None = None  # parámetro opcional
) -> TenenciaAcumulada:
    try:
        fecha_corte = fecha_corte or datetime.utcnow()

        tenencia = db.query(TenenciaAcumulada).filter_by(payment_method_id=payment_method_id).first()

        if tenencia:
            tenencia.importe_acumulado = importe_acumulado
            tenencia.fecha_corte = fecha_corte
        else:
            tenencia = TenenciaAcumulada(
                payment_method_id=payment_method_id,
                importe_acumulado=importe_acumulado,
                fecha_corte=fecha_corte,
            )
            db.add(tenencia)

        db.commit()
        db.refresh(tenencia)
        return tenencia

    except SQLAlchemyError as e:
        db.rollback()
        raise ActualizacionTenenciasFallida("Error al insertar o actualizar tenencia acumulada.") from e


def get_tenencias(db: Session):
    """
    Devuelve tenencias netas por medio de pago (ingresos - egresos), incluyendo su moneda.
    Mantiene la estructura original esperada por la vista.
    """
    from sqlalchemy import case

    rows = (
        db.query(
            PaymentMethod.id,
            PaymentMethod.name,
            PaymentMethod.currency,
            func.sum(
                case(
                    (MovimientoDinero.tipo == TipoMovimientoDinero.INGRESO, MovimientoDinero.importe),
                    (MovimientoDinero.tipo == TipoMovimientoDinero.EGRESO, -MovimientoDinero.importe),
                    else_=0,
                )
            ).label("amount")
        )
        .join(MovimientoDinero.metodo_pago)
        .group_by(PaymentMethod.id, PaymentMethod.name, PaymentMethod.currency)
        .all()
    )

    por_medio = [
        {
            "id": pm_id,
            "name": name,
            "currency": currency,
            "currency_label": CURRENCY_LABELS.get(currency, currency),
            "amount": float(amount),
        }
        for pm_id, name, currency, amount in rows
    ]

    return {"por_medio": por_medio}

def get_tenencias_convertidas(
    db: Session, target_currency: str, frankfurter_base_url: str
) -> tuple[list[dict], float, str | None]:
    """
    Devuelve las tenencias por método de pago, con montos convertidos a la moneda objetivo.
    """
    data = get_tenencias(db)
    por_medio = data["por_medio"]
    orig_currencies = {
        m["currency"] for m in por_medio if m["currency"] != target_currency
    }

    try:
        rates, error_msg = get_exchange_rates(
            base=target_currency, symbols=orig_currencies, api_url=frankfurter_base_url
        )
    except Exception as e:
        raise ConversionMonedaFallida("Error al obtener tasas de conversión de monedas.") from e

    total_converted = 0.0
    for m in por_medio:
        amt = m["amount"]
        if m["currency"] == target_currency:
            m["converted"] = round(amt, 2)
            total_converted += m["converted"]
        else:
            rate = rates.get(m["currency"])
            if rate:
                m["converted"] = round(amt / rate, 2)
                total_converted += m["converted"]
            else:
                m["converted"] = None

    return por_medio, total_converted, error_msg

def obtener_tenencias_delta_entre_fechas(
    db: Session,
    desde: datetime,
    hasta: datetime
) -> dict[int, float]:
    """
    Calcula el saldo neto (ingresos - egresos) por método de pago entre fechas.
    desde: fecha_corte_anterior (exclusivo)
    hasta: fecha_corte_actual (inclusivo)
    """
    rows = (
        db.query(
            MovimientoDinero.payment_method_id,
            func.sum(
                case(
                    (MovimientoDinero.tipo == TipoMovimientoDinero.INGRESO, MovimientoDinero.importe),
                    (MovimientoDinero.tipo == TipoMovimientoDinero.EGRESO, -MovimientoDinero.importe),
                    else_=0
                )
            ).label("delta")
        )
        .filter(
            MovimientoDinero.fecha > desde,
            MovimientoDinero.fecha <= hasta
        )
        .group_by(MovimientoDinero.payment_method_id)
        .all()
    )

    return {payment_method_id: float(delta or 0) for payment_method_id, delta in rows}

def sumar_acumulados_y_deltas(
    acumulados: list[TenenciaAcumulada],
    deltas: dict[int, float]
) -> dict[int, float]:
    """
    Suma el importe acumulado previo con el delta reciente para cada método de pago.
    Devuelve un nuevo dict con los saldos actualizados por payment_method_id.
    """
    resultado = {}

    # Primero agregamos los acumulados base
    for tenencia in acumulados:
        pm_id = tenencia.payment_method_id
        resultado[pm_id] = float(tenencia.importe_acumulado)

    # Luego sumamos los deltas (incluso si no existían en acumulados)
    for pm_id, delta in deltas.items():
        if pm_id in resultado:
            resultado[pm_id] += delta
        else:
            resultado[pm_id] = delta

    return resultado

def formatear_respuesta_para_vista(
    db: Session,
    saldos: dict[int, float]
) -> dict:
    """
    Devuelve una estructura con los saldos actualizados por medio de pago,
    incluyendo su información (nombre, moneda y etiqueta de moneda).
    """
    if not saldos:
        return {"por_medio": []}

    # Obtener métodos de pago asociados
    metodos = (
        db.query(PaymentMethod)
        .filter(PaymentMethod.id.in_(saldos.keys()))
        .all()
    )

    por_medio = []
    for metodo in metodos:
        pm_id = metodo.id
        por_medio.append({
            "id": pm_id,
            "name": metodo.name,
            "currency": metodo.currency,
            "currency_label": CURRENCY_LABELS.get(metodo.currency, metodo.currency),
            "amount": round(saldos.get(pm_id, 0.0), 2)
        })

    return {"por_medio": por_medio}