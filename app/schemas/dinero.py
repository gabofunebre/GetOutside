from pydantic import BaseModel, ConfigDict
from datetime import datetime

from .pago import PaymentMethodOut
from .emus import TipoMovimientoDinero


class MovimientoDineroBase(BaseModel):
    fecha: datetime
    concepto: str
    importe: float
    tipo: TipoMovimientoDinero
    payment_method_id: int


class MovimientoDineroCreate(MovimientoDineroBase):
    pass


class MovimientoDineroOut(MovimientoDineroBase):
    id: int
    creado_en: datetime
    metodo_pago: PaymentMethodOut

    model_config = ConfigDict(from_attributes=True)


class TenenciaAcumuladaBase(BaseModel):
    payment_method_id: int
    importe_acumulado: float
    fecha_corte: datetime


class TenenciaAcumuladaCreate(TenenciaAcumuladaBase):
    pass


class TenenciaAcumuladaOut(TenenciaAcumuladaBase):
    metodo_pago: PaymentMethodOut  # incluir solo si vas a exponer el método de pago
    model_config = ConfigDict(from_attributes=True)
