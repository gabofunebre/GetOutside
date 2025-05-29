# --- Imports ---

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from sqlalchemy.exc import SQLAlchemyError

from app.models.dinero import MovimientoDinero
from app.models.enums import TipoMovimientoDinero
from app.models.dinero import TenenciaAcumulada
from app.models.ventas import PaymentMethod
from app.core.currencies import CURRENCY_LABELS
from app.exceptions.dinero import ActualizacionTenenciasFallida, ConsultaTenenciasFallida
from app.core.currencies import get_exchange_rates
from app.exceptions.dinero import ConversionMonedaFallida


# === BLOQUE PRINCIPAL ===
# get_tenencias: función principal del módulo, orquesta todo el flujo.

def get_tenencias(db: Session) -> dict:
    """
    Devuelve tenencias netas por medio de pago (ingresos - egresos), incluyendo su moneda.
    Calcula el saldo actualizado a partir de la última fecha de corte registrada y actualiza la tabla acumulada.
    """
    fecha_corte_actual = datetime.utcnow()

    # Paso 1: Leer tenencias acumuladas
    acumulados = leer_tenencias_acumuladas(db)

    # Paso 2: Obtener la fecha de corte anterior (máxima registrada)
    if acumulados:
        fecha_corte_anterior = max(t.fecha_corte for t in acumulados)
    else:
        # Si no hay acumulados previos, usamos una fecha de inicio arbitraria para incluir todos los movimientos
        fecha_corte_anterior = datetime.min

    # Paso 3: Obtener movimientos recientes desde la fecha de corte anterior hasta ahora
    deltas = obtener_tenencias_delta_entre_fechas(db, fecha_corte_anterior, fecha_corte_actual)

    # Paso 4: Sumar acumulados anteriores + deltas recientes
    nuevos_saldos = sumar_acumulados_y_deltas(acumulados, deltas)

    # Paso 5: Guardar los nuevos acumulados en la tabla (actualiza fecha_corte a ahora)
    if deltas:
        for pm_id, saldo in nuevos_saldos.items():
            upsert_tenencia_acumulada(db, payment_method_id=pm_id, importe_acumulado=saldo, fecha_corte=fecha_corte_actual)

    # Paso 6: Formatear y devolver la respuesta para la vista
    return formatear_respuesta_para_vista(db, nuevos_saldos)

# === FUNCIONES CRUD / DB ===
# Operaciones básicas con la tabla TenenciaAcumulada.

def leer_tenencias_acumuladas(db: Session) -> list[TenenciaAcumulada]:
    """Devuelve todas las tenencias acumuladas registradas."""
    try:
        return db.query(TenenciaAcumulada).all()
    except SQLAlchemyError as e:
        raise ConsultaTenenciasFallida("Error al leer tenencias acumuladas.") from e


def upsert_tenencia_acumulada(
    db: Session,
    payment_method_id: int,
    importe_acumulado: float,
    fecha_corte: datetime | None = None
) -> TenenciaAcumulada:
    """
    Inserta o actualiza la tenencia acumulada para un método de pago.
    """
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

# === FUNCIONES DE CÁLCULO ===
# Obtienen y procesan los saldos desde los movimientos.

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
            MovimientoDinero.creado_en  > desde,
            MovimientoDinero.creado_en  <= hasta
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

    for tenencia in acumulados:
        pm_id = tenencia.payment_method_id
        resultado[pm_id] = float(tenencia.importe_acumulado)

    for pm_id, delta in deltas.items():
        if pm_id in resultado:
            resultado[pm_id] += delta
        else:
            resultado[pm_id] = delta

    return resultado


# === FORMATO DE RESPUESTA ===
# Arma el resultado para ser enviado a la vista.

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


# === CONVERSIÓN DE MONEDAS ===
# Convierte los montos a una moneda objetivo usando la API de tasas.

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
