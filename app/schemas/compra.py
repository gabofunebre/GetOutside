from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.schemas.archivo import ArchivoOut
from app.schemas.pago import PaymentMethodOut


class CompraBase(BaseModel):
    fecha: datetime
    concepto: str
    monto: float
    archivo_id: Optional[int] = None
    payment_method_id: int


class CompraCreate(CompraBase):
    pass


class CompraOut(CompraBase):
    id: int
    archivo: Optional[ArchivoOut] = None
    payment_method: PaymentMethodOut

    model_config = ConfigDict(from_attributes=True)
