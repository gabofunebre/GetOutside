from pydantic import BaseModel, ConfigDict, constr


class PaymentMethodBase(BaseModel):
    """
    Campos base para crear o actualizar métodos de pago.
    """

    name: str  # Nombre del medio (p.ej. "Tarjeta")


class PaymentMethodCreate(PaymentMethodBase):
    """
    Esquema para creación de método de pago, añade moneda ISO.
    """

    currency: constr(min_length=3, max_length=3)  # ISO 4217


class PaymentMethodOut(PaymentMethodBase):
    """
    Salida de método de pago con ID y moneda.
    """
    id: int
    name: str
    currency: str

    class Config:
        orm_mode = True


class PagoCreate(BaseModel):
    """
    Entrada de pago: método y monto.
    """

    payment_method_id: int  # ID del medio de pago utilizado
    amount: float  # Monto pagado


class PagoOut(PagoCreate):
    """
    Salida de un pago, incluye detalle del medio de pago.
    """

    metodo: PaymentMethodOut  # Objeto anidado del medio

    model_config = ConfigDict(from_attributes=True)
