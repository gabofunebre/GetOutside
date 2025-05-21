from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pydantic import ConfigDict  # necesario en Pydantic v2

# --- Productos ---
class ProductoBase(BaseModel):
    codigo_getoutside: str
    descripcion: str
    catalogo_id: int
    precio_venta: float

class ProductoCreate(ProductoBase):
    stock_actual: int

class ProductoOut(BaseModel):
    id: int
    codigo_getoutside: str
    descripcion: str
    precio_venta: float
    stock_actual: int

    model_config = ConfigDict(from_attributes=True)

# --- Ventas / Pagos / Descuentos ---
class DetalleVentaIn(BaseModel):
    codigo_getoutside: str
    cantidad: int
    precio_unitario: float

class DetalleVentaOut(DetalleVentaIn):
    subtotal: float
    class Config:
        orm_mode = True

class PagoCreate(BaseModel):
    payment_method_id: int
    amount: float

class PaymentMethodBase(BaseModel):
    name: str

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodOut(PaymentMethodBase):
    id: int
    class Config:
        orm_mode = True

class PagoOut(PagoCreate):
    metodo: PaymentMethodOut
    class Config:
        orm_mode = True

class DescuentoCreate(BaseModel):
    concepto: str
    amount: float

class DescuentoOut(DescuentoCreate):
    class Config:
        orm_mode = True

class VentaCreate(BaseModel):
    detalles: List[DetalleVentaIn]
    pagos:    List[PagoCreate]
    descuentos: Optional[List[DescuentoCreate]] = []

class VentaOut(BaseModel):
    id: int
    fecha: datetime
    total: float
    detalles: List[DetalleVentaOut]
    pagos:    List[PagoOut]
    descuentos: List[DescuentoOut]
    class Config:
        orm_mode = True

# --- Catálogos ---
class CatalogoBase(BaseModel):
    filename: str

class CatalogoCreate(CatalogoBase):
    pass

class Catalogo(CatalogoBase):
    id: int
    filepath: str
    uploaded_at: datetime
    class Config:
        orm_mode = True
