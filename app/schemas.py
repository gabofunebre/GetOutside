# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Productos ---
class ProductoBase(BaseModel):
    codigo_getoutside: str
    codigo_mercaderia: str
    tipo: str                               # ← Nuevo campo obligatorio
    descripcion: Optional[str] = None         # ← Nuevo campo opcional
    color_prenda: Optional[str] = None
    proceso_aplicado: Optional[str] = None
    diseno_aplicado: Optional[str] = None
    variante_diseno: Optional[str] = None
    talle: Optional[str] = None
    precio_venta: float

class ProductoCreate(ProductoBase):
    stock_actual: int

class ProductoOut(ProductoBase):
    stock_actual: int
    class Config:
        orm_mode = True

# --- Ventas / Pagos (sin cambios) ---
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

class PagoOut(PagoCreate):
    metodo: str
    class Config:
        orm_mode = True

class VentaCreate(BaseModel):
    detalles: List[DetalleVentaIn]
    pagos:    List[PagoCreate]

class VentaOut(BaseModel):
    id: int
    fecha: datetime
    total: float
    detalles: List[DetalleVentaOut]
    pagos:    List[PagoOut]
    class Config:
        orm_mode = True

# --- Métodos de Pago ---
class PaymentMethodBase(BaseModel):
    name: str

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodOut(PaymentMethodBase):
    id: int
    class Config:
        orm_mode = True
