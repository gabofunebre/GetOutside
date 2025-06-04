from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

from app.schemas.pago import PagoCreate, PagoOut, PaymentMethodOut
from app.schemas.producto import ProductoOut


class DetalleVentaIn(BaseModel):
    """
    Entrada de detalle de venta: referencia por ID de producto.
    """

    producto_id: int  # ID del producto vendido
    cantidad: int  # Cantidad vendida
    precio_unitario: float  # Precio aplicado por unidad


class DetalleVentaOut(DetalleVentaIn):
    """
    Esquema de salida para detalle de venta, con subtotal calculado.
    """

    subtotal: float  # cantidad * precio_unitario

    model_config = ConfigDict(from_attributes=True)


class DescuentoCreate(BaseModel):
    """
    Entrada de descuento aplicado a la venta.
    """

    concepto: str  # Descripción del descuento
    amount: float  # Monto descontado


class DescuentoOut(DescuentoCreate):
    """
    Salida de descuento.
    """

    model_config = ConfigDict(from_attributes=True)


class VueltoCreate(BaseModel):
    """Entrada de vuelto: moneda y monto devuelto."""

    payment_method_id: int
    amount: float


class VueltoOut(VueltoCreate):
    """Salida de vuelto con detalle del medio de pago."""

    metodo: PaymentMethodOut

    model_config = ConfigDict(from_attributes=True)


class VentaCreate(BaseModel):
    """
    Entrada para crear una venta con detalles, pagos y descuentos.
    """

    detalles: List[DetalleVentaIn]  # Lista de ítems vendidos
    pagos: List[PagoCreate]  # Lista de pagos recibidos
    descuentos: Optional[List[DescuentoCreate]] = []  # Descuentos opcionales
    fecha: datetime
    vueltos: Optional[List[VueltoCreate]] = []  # Cambio entregado


class VentaOut(BaseModel):
    """
    Salida completa de una venta registrada.
    """

    id: int  # ID de la venta
    fecha: datetime  # Fecha y hora de la venta
    total: float  # Total neto de la venta
    detalles: List[DetalleVentaOut]  # Detalles con subtotales
    pagos: List[PagoOut]  # Pagos detallados
    descuentos: List[DescuentoOut]  # Descuentos aplicados
    vueltos: List[VueltoOut]  # Vueltos entregados

    model_config = ConfigDict(from_attributes=True)


class VentaFilterParams(BaseModel):
    "parametros para filtrar una venta"

    start: Optional[str] = None
    end: Optional[str] = None
    payment_method_id: Optional[str] = None
    codigo_getoutside: Optional[str] = None
